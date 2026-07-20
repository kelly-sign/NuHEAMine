"""
feature_extractor.py

Light-weight, weight-based feature extractor for tabular data.

Supports:
  - GBDT / LightGBM  (feature importance → top-k)
  - Lasso / ElasticNet  (absolute coefficient → top-k)

The extractor is **stateless** during inference: once fitted,
it simply keeps the indices of the selected features and slices
any new matrix accordingly.

Maintained as part of the NuHEAMine project.
Date  : 2025-08-23
Version: 1.1
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Iterable, List, Literal, Optional, Union,Dict,Any
from sklearn.pipeline import Pipeline
import joblib
import numpy as np
import optuna
import pandas as pd
import lightgbm as lgb
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import (
    ElasticNet,
    LassoCV,
    Lasso,
    LinearRegression,
    LogisticRegression,
)
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import KFold, check_cv
from sklearn.base import clone
from sklearn.utils import resample
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams.update({
    "font.sans-serif": ["SimHei"],
    "axes.unicode_minus": False,
    "axes.labelsize": 15,
    "axes.titlesize": 16,
    "lines.linewidth": 3,
    "lines.color": "#5B9BD5"
})
# 关闭 optuna 的详细日志，只保留进度条
optuna.logging.set_verbosity(optuna.logging.WARNING)

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def select_features_by_correlation_to_target(
    X: pd.DataFrame,
    y: pd.Series,
    threshold: float,
) -> pd.DataFrame:
    """
    Keep features whose absolute correlation with the target exceeds `threshold`.

    Parameters
    ----------
    X : pd.DataFrame
        Input features.
    y : pd.Series
        Target vector.
    threshold : float
        Minimum absolute correlation required.

    Returns
    -------
    pd.DataFrame
        Filtered feature matrix.
    """
    corr = X.corrwith(y).abs()
    keep_cols = corr[corr > threshold].index.tolist()
    return X[keep_cols]


def drop_highly_correlated_columns(
    X: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """
    Drop columns that are highly correlated with any other column.

    Parameters
    ----------
    X : pd.DataFrame
        Input features.
    threshold : float
        Correlation threshold above which one of the two columns is removed.

    Returns
    -------
    pd.DataFrame
        Feature matrix with multicollinearity reduced.
    """
    corr = X.corr().abs()
    upper = corr.where(
        np.triu(np.ones(corr.shape), k=1).astype(bool)
    )
    to_drop = [c for c in upper.columns if any(upper[c] > threshold)]
    return X.drop(columns=to_drop)


def select_top_variance_features(
    X: pd.DataFrame,
    proportion: float = 0.85,
) -> pd.DataFrame:
    """
    Select the top `proportion` fraction of features with highest variance.

    Parameters
    ----------
    X : pd.DataFrame
        Input features.
    proportion : float, default 0.85
        Fraction of features to retain.

    Returns
    -------
    pd.DataFrame
        Filtered feature matrix.
    """
    variances = X.var().sort_values(ascending=False)
    n_keep = max(1, int(proportion * len(variances)))
    keep_cols = variances.index[:n_keep].tolist()
    return X[keep_cols]


# ------------------------------------------------------------------
# Core classes
# ------------------------------------------------------------------
class FeatureExtractor:
    """
    Model-based feature selector.

    Parameters
    ----------
    method : {'lgbm', 'gbdt', 'lasso', 'elastic'}, default 'lgbm'
        Algorithm used to rank features.
    k : int or float, default 20
        Number (or fraction) of top features to keep.
    n_trials : int, default 20
        Optuna trials for hyper-parameter tuning.
    task : {'auto', 'regression', 'classification'}, default 'auto'
        Task type. If 'auto', inferred from the target.
    **model_kwargs
        Extra arguments passed to the underlying estimator.
    """

    def __init__(
        self,
        method: Literal["lgbm", "gbdt", "lasso", "elastic"] = "lgbm",
        k: Union[int, float] = 20,
        n_trials: int = 20,
        task: Literal["auto", "regression", "classification"] = "auto",
        **model_kwargs,
    ) -> None:
        self.method = method
        self.k = k
        self.n_trials = n_trials
        self.task = task
        self.model_kwargs = model_kwargs
        self.selected_cols_: Optional[List[str]] = None
        self.report_: Optional[dict] = None

    # ------------------------------------------------------------------
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "FeatureExtractor":
        """Fit the selector and store chosen feature names."""
        if not isinstance(X, pd.DataFrame):
            raise TypeError("X must be a pandas.DataFrame")
        if not isinstance(y, pd.Series):
            y = pd.Series(y, index=X.index)

        random_state = int(self.model_kwargs.pop("random_state", 42))
        bootstrap_rounds = int(self.model_kwargs.pop("bootstrap_rounds", 50))
        optuna_trials = int(self.model_kwargs.pop("optuna_trials", self.n_trials))
        n_features = X.shape[1]

        # Infer task
        if self.task == "auto":
            is_classification = y.nunique() <= 20
        else:
            is_classification = self.task == "classification"

        score_fn = roc_auc_score if is_classification else r2_score

        # ---------- LightGBM / GBDT ----------
        if self.method in {"lgbm", "gbdt"}:
            Model = lgb.LGBMClassifier if is_classification else lgb.LGBMRegressor
            importances = np.zeros(n_features)

            for b in range(bootstrap_rounds):
                Xb, yb = resample(X, y, random_state=random_state + b)

                def objective(trial):
                    params = {
                        "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                        "learning_rate": trial.suggest_float(
                            "learning_rate", 1e-3, 0.3, log=True
                        ),
                        "num_leaves": trial.suggest_int("num_leaves", 7, 63),
                        "min_child_samples": trial.suggest_int(
                            "min_child_samples", 1, 10
                        ),
                        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                        "colsample_bytree": trial.suggest_float(
                            "colsample_bytree", 0.6, 1.0
                        ),
                        "random_state": random_state,
                        "verbosity": -1,
                    }
                    model = Model(**params)
                    cv_scores = []
                    kfold = KFold(
                        3, shuffle=True, random_state=random_state + b
                    )
                    for tr, va in kfold.split(Xb):
                        model.fit(Xb.iloc[tr], yb.iloc[tr])
                        if is_classification:
                            y_pred = model.predict_proba(Xb.iloc[va])[:, 1]
                        else:
                            y_pred = model.predict(Xb.iloc[va])
                        cv_scores.append(score_fn(yb.iloc[va], y_pred))
                    return np.mean(cv_scores)

                study = optuna.create_study(direction="maximize")
                study.optimize(objective, n_trials=optuna_trials, show_progress_bar=True)

                best_model = Model(
                    **study.best_params,
                    random_state=random_state,
                    verbosity=-1,
                )
                best_model.fit(Xb, yb)
                importances += best_model.feature_importances_

            importances /= bootstrap_rounds
            indices = np.argsort(importances)[::-1]

        # ---------- Lasso ----------
        elif self.method == "lasso":
            freq = np.zeros(n_features)
            for b in range(bootstrap_rounds):
                Xb, yb = resample(X, y, random_state=random_state + b)

                def objective(trial):
                    alpha = trial.suggest_float("alpha", 1e-4, 1.0, log=True)
                    model = Lasso(alpha=alpha, max_iter=5000, random_state=random_state)
                    cv_scores = []
                    kfold = KFold(
                        3, shuffle=True, random_state=random_state + b
                    )
                    for tr, va in kfold.split(Xb):
                        model.fit(Xb.iloc[tr], yb.iloc[tr])
                        cv_scores.append(r2_score(yb.iloc[va], model.predict(Xb.iloc[va])))
                    return np.mean(cv_scores)

                study = optuna.create_study(direction="maximize")
                study.optimize(objective, n_trials=optuna_trials, show_progress_bar=True)

                best_model = Lasso(
                    alpha=study.best_params["alpha"],
                    max_iter=5000,
                    random_state=random_state,
                )
                best_model.fit(Xb, yb)
                freq += np.abs(best_model.coef_) > 1e-6

            freq /= bootstrap_rounds
            indices = np.where(freq >= 0.3)[0]

        # ---------- ElasticNet ----------
        elif self.method == "elastic":
            freq = np.zeros(n_features)
            for b in range(bootstrap_rounds):
                Xb, yb = resample(X, y, random_state=random_state + b)

                def objective(trial):
                    alpha = trial.suggest_float("alpha", 1e-4, 1.0, log=True)
                    l1_ratio = trial.suggest_float("l1_ratio", 0.1, 0.9)
                    model = ElasticNet(
                        alpha=alpha,
                        l1_ratio=l1_ratio,
                        max_iter=5000,
                        random_state=random_state,
                    )
                    cv_scores = []
                    kfold = KFold(
                        3, shuffle=True, random_state=random_state + b
                    )
                    for tr, va in kfold.split(Xb):
                        model.fit(Xb.iloc[tr], yb.iloc[tr])
                        cv_scores.append(r2_score(yb.iloc[va], model.predict(Xb.iloc[va])))
                    return np.mean(cv_scores)

                study = optuna.create_study(direction="maximize")
                study.optimize(objective, n_trials=optuna_trials, show_progress_bar=True)

                best_model = ElasticNet(
                    **study.best_params,
                    max_iter=5000,
                    random_state=random_state,
                )
                best_model.fit(Xb, yb)
                freq += np.abs(best_model.coef_) > 1e-6

            freq /= bootstrap_rounds
            indices = np.where(freq >= 0.6)[0]

        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Determine k
        if isinstance(self.k, float):
            k = max(1, int(self.k * len(indices)))
        else:
            k = int(self.k)
        self.selected_cols_ = X.columns[indices[:k]].tolist()

        # Final CV score with best params
        final_scores = []
        kfold = KFold(3, shuffle=True, random_state=random_state)
        for tr, va in kfold.split(X):
            if self.method in {"lgbm", "gbdt"}:
                model = Model(
                    **study.best_params,
                    random_state=random_state,
                    verbosity=-1,
                )
            elif self.method == "lasso":
                model = Lasso(
                    alpha=study.best_params["alpha"],
                    max_iter=5000,
                    random_state=random_state,
                )
            else:  # elastic
                model = ElasticNet(
                    **study.best_params,
                    max_iter=5000,
                    random_state=random_state,
                )

            model.fit(X.iloc[tr], y.iloc[tr])
            if is_classification:
                y_pred = model.predict_proba(X.iloc[va])[:, 1]
            else:
                y_pred = model.predict(X.iloc[va])
            final_scores.append(score_fn(y.iloc[va], y_pred))

        # Build report
        self.report_ = {
            "features": self.selected_cols_,
            "importance": (
                importances[indices[:k]].tolist()
                if self.method in {"lgbm", "gbdt"}
                else freq[indices[:k]].tolist()
            ),
            "cv_metric_mean": float(np.mean(final_scores)),
            "task": "classification" if is_classification else "regression",
            "metric": "roc_auc" if is_classification else "r2",
        }
        return self

    # ------------------------------------------------------------------
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return selected features only."""
        if self.selected_cols_ is None:
            raise RuntimeError("Call .fit() first.")
        return X[self.selected_cols_]

    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Fit and return transformed data."""
        return self.fit(X, y).transform(X)

    def get_feature_names_out(
        self, input_features: Optional[Iterable[str]] = None
    ) -> List[str]:
        """Return list of selected feature names."""
        if self.selected_cols_ is None:
            raise RuntimeError("Call .fit() first.")
        return self.selected_cols_

    def print_report(self) -> None:
        """Print a concise summary of the selection process."""
        if self.report_ is None:
            raise RuntimeError("Call .fit() first.")
        print("=== FeatureExtractor Report ===")
        print(f"Task      : {self.report_['task']}")
        print(f"Metric    : {self.report_['metric']}")
        print(f"CV score  : {self.report_['cv_metric_mean']:.4f}")
        print("Top features (↓ importance):")
        for name, imp in zip(self.report_["features"], self.report_["importance"]):
            print(f"  {name:<12} {imp:.4f}")
        print("===============================")


# ------------------------------------------------------------------
# Pipeline
# ------------------------------------------------------------------
def feature_selection_pipeline(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    task: Literal["regression", "classification"] = "regression",
    corr_ratio: float = 0.5,
    corr_threshold: float = 0.85,
    max_features: Union[int, float] = 0.3,
    cv: int = 5,
    cache_dir: Optional[str] = None,
) -> List[str]:
    """
    Two-stage feature selection.

    1. Univariate filter (correlation / F-test).
    2. Remove multicollinear features.
    3. Forward selection with cross-validation.

    Parameters
    ----------
    X : pd.DataFrame
        Input features.
    y : pd.Series
        Target vector.
    task : {'regression', 'classification'}, default 'regression'
        Type of supervised learning task.
    corr_ratio : float, default 0.5
        Fraction of features to keep after univariate filter.单个特征与目标变量的相关性
    corr_threshold : float, default 0.85
        Correlation threshold for removing collinear features.高度相关的特征
    max_features : int or float, default 0.3
        Maximum number (or fraction) of features to select.
    cv : int, default 5
        Number of cross-validation folds.
    cache_dir : str or None, default None
        Directory to cache results. If None, caching is disabled.

    Returns
    -------
    List[str]
        Names of selected features.
    """
    # Cache handling
    if cache_dir:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        cache_key = joblib.hash(
            (
                X.values.tobytes(),
                y.values.tobytes(),
                task,
                corr_ratio,
                corr_threshold,
                max_features,
                cv,
            )
        )
        cache_file = Path(cache_dir) / f"fs_{cache_key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())

    # 1) Univariate filter
    k_univariate = max(1, int(corr_ratio * X.shape[1]))
    score_func = f_classif if task == "classification" else f_regression
    selector = SelectKBest(score_func, k=k_univariate)
    selector.fit(X, y)
    candidate_cols = X.columns[selector.get_support()].tolist()

    # 2) Remove collinear features
    corr = X[candidate_cols].corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [c for c in upper.columns if any(upper[c] > corr_threshold)]
    candidate_cols = [c for c in candidate_cols if c not in to_drop]

    # 3) Forward selection
    if isinstance(max_features, float):
        max_features = max(1, int(max_features * len(candidate_cols)))
    max_features = min(max_features, len(candidate_cols))

    scorer = roc_auc_score if task == "classification" else r2_score
    model = (
        LogisticRegression(max_iter=2000)
        if task == "classification"
        else LinearRegression()
    )
    cv_obj = check_cv(cv, y, classifier=(task == "classification"))

    selected: List[str] = []
    best_score = -np.inf
    remaining = candidate_cols.copy()
    cv_history = []  # 记录 (已选特征数, 当前最佳CV分数)
    while len(selected) < max_features and remaining:
        trial_scores = []
        for col in remaining:
            features = selected + [col]
            score = 0.0
            X_sub = X[features].values
            for tr, va in cv_obj.split(X_sub, y):
                m = clone(model).fit(X_sub[tr], y.iloc[tr])
                if task == "classification":
                    y_pred = m.predict_proba(X_sub[va])[:, 1]
                else:
                    y_pred = m.predict(X_sub[va])
                score += scorer(y.iloc[va], y_pred)
            trial_scores.append(score / cv_obj.get_n_splits())

        best_idx = int(np.argmax(trial_scores))
        current_best = trial_scores[best_idx]  # 本轮能达到的最好CV分数
        # 只有提升才加入；也可加一个微小容忍 tol 避免浮点抖动
        tol = 1e-6
        if current_best > best_score + tol:
            best_score = current_best
            best_col = remaining[best_idx]
            selected.append(best_col)
            remaining.remove(best_col)

            # 记录本步历史：当前已选个数 & 最佳CV分数
            cv_history.append((len(selected), float(best_score)))
        else:
            break
    # --- while 结束后，打印趋势 ---
    if scorer is r2_score and len(cv_history) > 0:
        print("\n[Forward Selection] CV R² 趋势：")
        for i, (k, s) in enumerate(cv_history):
            if i == 0:
                print(f"  选到 {k:>2d} 个特征：CV R² = {s:.4f}")
            else:
                delta = s - cv_history[i - 1][1]
                arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
                print(f"  选到 {k:>2d} 个特征：CV R² = {s:.4f}  ({arrow} {delta:+.4f})")
    # —— 前向选择曲线：强制样式隔离 + 固定颜色/线宽/字体 ——
    try:
        if len(cv_history) > 0:
            ks = [k for k, _ in cv_history]
            ss = [s for _, s in cv_history]

            # 1) 彻底重置外部样式影响
            plt.rcdefaults()  # 恢复 Matplotlib 默认
            try:
                sns.reset_orig()  # 恢复 seaborn 默认（若之前 set_theme 过）
            except Exception:
                pass

            # 2) 仅对这张图生效的 rc 设置（中文+粗体）
            with plt.rc_context({
                "font.sans-serif": ["SimHei"],  # 中文黑体
                "axes.unicode_minus": False,  # 正常显示负号
                "axes.labelsize": 13,
                "axes.titlesize": 14,
                "axes.linewidth": 1.2,
                "xtick.labelsize": 12,
                "ytick.labelsize": 12,
            }):
                fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=140)
                # 3) 明确指定你想要的样式
                ax.plot(ks, ss, marker="o", markersize=5,
                        linewidth=2.2, color="#FFBBC8")  # 颜色固定
                ax.set_xlabel("Number of selected feature variables", fontsize=15, fontweight='bold')
                ax.set_ylabel("CV R²", fontsize=15, fontweight='bold')
                #ax.set_title("前向选择：CV R² 趋势", fontweight="bold", pad=6)
                ax.grid(True, linestyle="--", alpha=0.3)
                ax.set_facecolor("white")

                fig.tight_layout()

                # 保存为 SVG/PNG 都行
                out_svg = "./Forward_Selection_CV_R2.svg"
                fig.savefig(out_svg, format="svg", bbox_inches="tight")
                print(f"[OK] 已保存：{out_svg} ")

                plt.show()
    except Exception:
        pass
    # Cache results
    if cache_dir:
        cache_file.write_text(json.dumps(selected))
    return selected

def lasso_refine_features(
    X: pd.DataFrame,
    y: pd.Series,
    base_features: List[str],
    *,
    max_keep: int = 12,
    cv: int = 10,
    random_state: int = 42,
    alphas: Optional[np.ndarray] = None,
    alpha_multiplier: float = 1.5,
    coef_tol: float = 1e-8,
    return_report: bool = True,
) -> Dict[str, Any]:
    """
    在“已完成初筛”的特征集合上，使用 标准化 + LassoCV 做二次精炼。
    - 先用 LassoCV 选出 best alpha；
    - 为更保守、抑制过拟合，把 alpha 乘以 alpha_multiplier 再拟合一次；
    - 取非零系数特征；如数量过多，按 |coef| 排序截断到 max_keep。

    Parameters
    ----------
    X : DataFrame
        训练特征（未缩放的原始特征矩阵）。
    y : Series or 1d array
        训练标签（回归目标）。
    base_features : list[str]
        第一阶段筛选后保留下来的特征名列表。
    max_keep : int
        最多保留的特征数（进一步抑制过拟合）。
    cv : int
        LassoCV 的交叉验证折数。
    random_state : int
        随机种子。
    alphas : np.ndarray | None
        LassoCV 搜索的 alpha 网格。默认使用 logspace(-4,1,60)。
    alpha_multiplier : float
        “轻保守”系数（>1 会提高正则强度，防过拟合）。常用范围 1.2~2.0。
    coef_tol : float
        判断系数非零的阈值。
    return_report : bool
        若 True，返回包含细节的 dict；否则仅返回 {'features': [...]}

    Returns
    -------
    dict
        {
          "features": List[str],            # 最终入模特征
          "alpha_best": float,              # LassoCV 选出的最佳 alpha
          "alpha_used": float,              # 乘以 alpha_multiplier 后实际使用的 alpha
          "coef": np.ndarray,               # 对应最终模型的系数（与 base_features 对齐）
          "kept_mask": np.ndarray[bool],    # 非零掩码（与 base_features 对齐）
          "base_features": List[str]        # 输入的 base_features 备份
        }
    """
    if alphas is None:
        alphas = np.logspace(-4, 1, 60)

    # —— 安全性处理 ——
    X_local = X[base_features].copy()
    y_local = np.asarray(y).ravel()

    # 1) 标准化 + LassoCV（交叉验证自动挑 alpha）
    lasso_cv = Pipeline([
        ("scaler", StandardScaler()),
        ("lasso", LassoCV(
            alphas=alphas,
            cv=cv,
            random_state=random_state,
            max_iter=5000,
            n_alphas=len(alphas),
            fit_intercept=True
        ))
    ])
    lasso_cv.fit(X_local, y_local)

    alpha_best = float(lasso_cv.named_steps["lasso"].alpha_)
    alpha_used = float(alpha_best * alpha_multiplier)

    # 2) 用更保守的 alpha 重新拟合
    lasso_final = Pipeline([
        ("scaler", StandardScaler()),
        ("lasso", Lasso(alpha=alpha_used, max_iter=5000, random_state=random_state))
    ])
    lasso_final.fit(X_local, y_local)

    coef = lasso_final.named_steps["lasso"].coef_
    kept_mask = np.abs(coef) > coef_tol
    kept_names = list(pd.Index(base_features)[kept_mask])

    # 3) 如数量仍过多，按 |coef| 截断
    if len(kept_names) > max_keep:
        order = np.argsort(-np.abs(coef[kept_mask]))
        kept_names = list(pd.Index(kept_names)[order[:max_keep]])

    result = {
        "features": kept_names
    }
    if return_report:
        result.update({
            "alpha_best": alpha_best,
            "alpha_used": alpha_used,
            "coef": coef,
            "kept_mask": kept_mask,
            "base_features": list(base_features),
        })
    return result
