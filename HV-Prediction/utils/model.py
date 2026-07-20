import os
import joblib
import inspect
import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler
from typing import Union, List, Callable
#导入多种集成学习回归模型
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
    ExtraTreesRegressor,
)
from sklearn.gaussian_process import GaussianProcessRegressor
import lightgbm as lgb
from xgboost import XGBRegressor
from sklearn.linear_model import Ridge,ElasticNet
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Lasso
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
)
from sklearn.model_selection import LeaveOneOut,KFold,RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# 关闭 optuna 的详细日志，只保留进度条
optuna.logging.set_verbosity(optuna.logging.WARNING)
import logging
logging.getLogger('lightgbm').setLevel(logging.ERROR)
def rmse(y_true, y_pred):
    # 单独封装，避免在 mean_squared_error 上传 squared=False 参数
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))
def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
from scipy import optimize

def _lbfgs_with_maxiter(obj_func, initial_theta, bounds):
    # obj_func: 返回 (f, g) 的可微目标
    res = optimize.minimize(
        obj_func,
        initial_theta,
        method="L-BFGS-B",
        jac=True,
        bounds=bounds,
        options={"maxiter": 2000}  # 想多大就写多大
    )
    return res.x, res.fun

def objective(trial, model_name, X: pd.DataFrame, y: pd.Series, feature_index=None, n_splits=10):
    """Objective function for hyperparameter optimization using Optuna.

    Args:
        trial (optuna.Trial): Optuna trial object.
        model_name (str): Name of the model to optimize.
        X (pd.DataFrame): Feature set.
        y (pd.Series): Labels.
        n_splits (int): Number of splits for cross-validation.

    Returns:
        以“最大化 R2”为目标的 Optuna 目标函数。
        返回值: 平均 R2（越大越好）
    """
    seed = 42
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=3, random_state=seed)
    # loo = LeaveOneOut()
    scores = []

    # 如果传入了 feature_index，则只使用这些特征
    if feature_index is not None:
        X = X.iloc[:, feature_index] if isinstance(feature_index[0], int) \
            else X[feature_index]

    for train_index, val_index in cv.split(X):
        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
        y_train, y_val = y.iloc[train_index], y.iloc[val_index]
        trained = False  # ← 从这里开始，用你的新逻辑

        if model_name == "GPR":
            from sklearn.gaussian_process.kernels import (RBF, Matern, RationalQuadratic,ConstantKernel as C, WhiteKernel)
            from sklearn.exceptions import ConvergenceWarning
            import warnings
            xs = StandardScaler()
            X_tr_s = xs.fit_transform(X_train)
            X_va_s = xs.transform(X_val)
            p = X_train.shape[1]
            # 搜索空间同你现有的，只把 bounds 与 alpha 略调稳一些
            c_val = trial.suggest_float("c", 1e-2, 10.0, log=True)
            noise_level = trial.suggest_float("noise", 1e-5, 1e-1, log=True)
            alpha_val = trial.suggest_float("alpha", 1e-8, 1e-3, log=True)
            kernel_choice = trial.suggest_categorical("kernel", ["RBF", "Matern", "Matern+RQ"])
            matern_nu = trial.suggest_categorical("matern_nu", [0.5, 1.5, 2.5])
            rq_alpha = trial.suggest_float("rq_alpha", 1e-3, 1e2, log=True)  # 上界降到 1e2
            rq_ls = trial.suggest_float("rq_ls", 1e-2, 1e2, log=True)  # 上界降到 1e2
            # 对 ARD length_scale：在标准化后，length_scale 的有效范围可以收窄
            # 我们使用每维相同的初始值（np.ones * base），避免动态 categorical 报错
            ls_base = trial.suggest_float("ls_base", 0.1, 10.0, log=True)
            ls_bounds = (1e-2, 1e3)  # 上界保守但不是极大
            if kernel_choice == "RBF":
                base = RBF(length_scale=np.ones(p) * ls_base, length_scale_bounds=ls_bounds)
            elif kernel_choice == "Matern":
                base = Matern(length_scale=np.ones(p) * ls_base, length_scale_bounds=ls_bounds, nu=matern_nu)
            else:  # Matern + RQ
                base = (Matern(length_scale=np.ones(p) * ls_base, length_scale_bounds=ls_bounds, nu=matern_nu)
                        + RationalQuadratic(alpha=rq_alpha, length_scale=rq_ls))

            kernel = C(c_val, (1e-3, 1e3)) * base + WhiteKernel(noise_level=noise_level, noise_level_bounds=(1e-8, 1e1))

            # n_restarts 不要太大（每次优化代价高），选 0-6 或 0-3
            n_restarts = trial.suggest_int("n_restarts_optimizer", 0, 4)
            normalize_y = trial.suggest_categorical("normalize_y", [True, False])
            model = GaussianProcessRegressor(
                kernel=kernel,
                alpha=alpha_val,
                normalize_y=normalize_y,
                n_restarts_optimizer=int(n_restarts),
                optimizer="fmin_l_bfgs_b",
                random_state=seed,
                copy_X_train=False,
            )

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=ConvergenceWarning)
                model.fit(X_tr_s, np.asarray(y_train).ravel())

            y_pred = model.predict(X_va_s)
            trained = True
        elif model_name == "LGBM":
            model = lgb.LGBMRegressor(
                n_estimators=trial.suggest_int("n_estimators", 300, 2000),
                learning_rate=trial.suggest_float("learning_rate", 1e-3, 5e-2, log=True),
                num_leaves=trial.suggest_int("num_leaves", 8, 64),
                max_depth=trial.suggest_int("max_depth", 4, 6),
                min_data_in_leaf=trial.suggest_int("min_data_in_leaf", 10, 50),
                min_sum_hessian_in_leaf=trial.suggest_float("min_sum_hessian_in_leaf", 1e-2, 1.0, log=True),
                feature_fraction=trial.suggest_float("feature_fraction", 0.5, 1.0),
                bagging_fraction=trial.suggest_float("bagging_fraction", 0.5, 1.0),
                lambda_l1=trial.suggest_float("lambda_l1", 1e-6, 10.0, log=True),
                lambda_l2=trial.suggest_float("lambda_l2",  1e-6, 10.0, log=True),
                min_gain_to_split=trial.suggest_float("min_gain_to_split", 0.0, 1.0),
                bagging_freq=trial.suggest_int("bagging_freq", 0, 5),
                random_state=seed,
                n_jobs=1,
            )
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                eval_metric="rmse",
                callbacks=[lgb.early_stopping(100, verbose=False)]
            )
            best_it = getattr(model, "best_iteration_", None)
            if best_it is not None:
                y_pred = model.predict(X_val, num_iteration=best_it)
            else:
                y_pred = model.predict(X_val)
            trained = True
        elif model_name == "XGB":
            # 放在函数顶部有 import 就不用重复；否则补上：
            # from xgboost import XGBRegressor
            try:
                from xgboost.callback import EarlyStopping
                _have_es_cb = True
            except Exception:
                _have_es_cb = False

            model = XGBRegressor(
                n_estimators=trial.suggest_int("n_estimators", 800, 4000),
                max_depth=trial.suggest_int("max_depth", 3, 6),
                learning_rate=trial.suggest_float("learning_rate", 5e-4, 0.1, log=True),
                subsample=trial.suggest_float("subsample", 0.6, 0.9),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 0.9),
                reg_alpha=trial.suggest_float("reg_alpha", 1e-6, 5.0, log=True),
                reg_lambda=trial.suggest_float("reg_lambda", 1e-6, 5.0, log=True),
                min_child_weight=trial.suggest_float("min_child_weight", 5, 50.0, log=True),
                gamma=trial.suggest_float("gamma", 0.0, 5.0),
                objective="reg:squarederror",
                tree_method=trial.suggest_categorical("tree_method", ["auto", "hist"]),
                random_state=seed,
                n_jobs=1,  # 外层 joblib 并行时，里层建议单线程避免资源抢占
                eval_metric="rmse",
            )

            # ==== 版本自适应早停 ====
            fitted = False
            if _have_es_cb:
                try:
                    es_cb = EarlyStopping(rounds=50, save_best=True)
                    model.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        callbacks=[es_cb],
                        verbose=False
                    )
                    fitted = True
                except TypeError:
                    # 某些版本 sklearn wrapper 不支持 callbacks 关键字
                    pass

            if not fitted:
                try:
                    # 退回到大多数版本都支持的 early_stopping_rounds
                    model.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        early_stopping_rounds=50,
                        verbose=False
                    )
                    fitted = True
                except TypeError:
                    # 仍不支持：无早停训练
                    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
                    fitted = True

            # ==== 版本自适应预测（使用最佳迭代）====
            best_it = getattr(model, "best_iteration", None)
            if best_it is not None:
                # 优先新版 API
                try:
                    y_pred = model.predict(X_val, iteration_range=(0, best_it + 1))
                except TypeError:
                    # 旧版回退
                    y_pred = model.predict(X_val, ntree_limit=best_it + 1)
            else:
                # 有些版本只给 best_ntree_limit
                best_nt = getattr(model, "best_ntree_limit", None)
                if best_nt is not None:
                    try:
                        y_pred = model.predict(X_val, ntree_limit=best_nt)
                    except TypeError:
                        # 再次兜底
                        y_pred = model.predict(X_val)
                else:
                    y_pred = model.predict(X_val)

            trained = True
        elif model_name == "RFR":
            model = RandomForestRegressor(
                n_jobs=1,
                random_state=seed,
                n_estimators=trial.suggest_int("n_estimators", 10, 1000),
                max_depth=trial.suggest_int("max_depth", 5, 50),
                min_samples_split=trial.suggest_int("min_samples_split", 2, 25),
                min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            )
        elif model_name == "KNR":
            # KNN：扩大邻居范围 + 可选 uniform/ distance；限制为常用的 Minkowski(p=1/2)
            model = make_pipeline(StandardScaler(with_mean=True, with_std=True), KNeighborsRegressor(
                n_neighbors=trial.suggest_int("n_neighbors", 5, 60),  # 更大范围通常更稳健
                weights=trial.suggest_categorical("weights", ["uniform", "distance"]),
                p=trial.suggest_categorical("p", [1, 2]),  # 1=Manhattan, 2=Euclidean
                algorithm=trial.suggest_categorical("algorithm", ["auto", "kd_tree", "ball_tree"]),
                leaf_size=trial.suggest_int("leaf_size", 20, 60))
            )
        elif model_name == "SVR":
            # SVR：仅用 RBF（更常用也更稳），加入 epsilon，收紧 C 和 gamma 的对数范围
            # 注意：你已经对 X 做过标准化（X_train_scaled），这里不要再加 StandardScaler()
            model = make_pipeline(StandardScaler(), SVR(
                kernel="rbf",
                C=trial.suggest_float("C", 1e-2, 100.0, log=True),  # 过大 C 容易过拟合
                gamma=trial.suggest_float("gamma", 1e-4, 1e0, log=True),  # 对特征尺度敏感，log 搜索更稳
                epsilon=trial.suggest_float("epsilon", 1e-3, 0.5, log=True),  # 容错带可抑制过拟合
                tol=trial.suggest_float("tol", 1e-5, 1e-2, log=True),
                shrinking=trial.suggest_categorical("shrinking", [True, False]),
                cache_size=300)
            )
        # elif model_name == "Lasso":
        #     model = Lasso(
        #         alpha=trial.suggest_float("alpha", 1e-6, 10.0, log=True),  # L1强度，越大越稀疏
        #         max_iter=trial.suggest_int("max_iter", 1000, 20000),
        #         tol=trial.suggest_float("tol", 1e-6, 1e-2, log=True),
        #         selection=trial.suggest_categorical("selection", ["cyclic", "random"]),
        #         fit_intercept=trial.suggest_categorical("fit_intercept", [True, False]),
        #         random_state=seed  # 仅当 selection='random' 时起作用；其余情况忽略
        #     )
        # elif model_name == "DTR":
        #     model = DecisionTreeRegressor(
        #         random_state=seed,
        #         max_depth=trial.suggest_int("max_depth", 3, 15),
        #         min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
        #         min_samples_leaf=trial.suggest_int("min_samples_leaf", 2, 10),
        #         max_leaf_nodes=trial.suggest_int("max_leaf_nodes", 4, 20),
        #     )
        # elif model_name == "ETR":
        #     model = ExtraTreesRegressor(
        #         n_estimators=trial.suggest_int("n_estimators", 500, 4000),
        #         max_depth=trial.suggest_int("max_depth", 3, 20),
        #         min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
        #         min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
        #         bootstrap=trial.suggest_categorical("bootstrap", [False, True]),
        #         random_state=seed,
        #         n_jobs=-1,
        #     )
        #     model.fit(X_train, y_train)
        #     y_pred = model.predict(X_val)
        # elif model_name == "GBR":
        #     model = GradientBoostingRegressor(
        #         n_estimators=trial.suggest_int("n_estimators", 500, 4000),
        #         learning_rate=trial.suggest_float("learning_rate", 5e-4, 0.1, log=True),
        #         max_depth=trial.suggest_int("max_depth", 2, 8),
        #         min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
        #         min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
        #         # sklearn 风格早停（内部基于 training 再切 validation_fraction）
        #         n_iter_no_change=trial.suggest_int("n_iter_no_change", 20, 100),
        #         validation_fraction=trial.suggest_float("validation_fraction", 0.1, 0.3),
        #         tol=trial.suggest_float("tol", 1e-5, 1e-3, log=True),
        #         random_state=seed,
        #     )
        #     model.fit(X_train, y_train)
        #     y_pred = model.predict(X_val)
        # elif model_name == "Ridge":
        #     model = Ridge(
        #         random_state=seed,
        #         alpha=trial.suggest_float("alpha", 1e-4, 100, log=True),
        #         max_iter=trial.suggest_int("max_iter", 100, 2000),
        #         tol=trial.suggest_float("tol", 1e-6, 1e-2, log=True),
        #     )
        # elif model_name == "AdaBoost":
        #     model = AdaBoostRegressor(
        #         estimator=DecisionTreeRegressor(
        #             max_depth=trial.suggest_int("dt_max_depth", 1, 6),
        #             min_samples_split=trial.suggest_int("dt_min_samples_split", 2, 20),
        #             min_samples_leaf=trial.suggest_int("dt_min_samples_leaf", 1, 10),
        #             random_state=seed,
        #         ),
        #         n_estimators=trial.suggest_int("n_estimators", 50, 1000),
        #         learning_rate=trial.suggest_float("learning_rate", 1e-3, 1.0, log=True),
        #         loss=trial.suggest_categorical("loss", ["linear", "square", "exponential"]),
        #         random_state=seed,
        #     )
        # elif model_name == "ElasticNet":
        #     model = ElasticNet(
        #         alpha=trial.suggest_float("alpha", 1e-4, 100.0, log=True),
        #         l1_ratio=trial.suggest_float("l1_ratio", 0.0, 1.0),
        #         max_iter=trial.suggest_int("max_iter", 1000, 10000),
        #         tol=trial.suggest_float("tol", 1e-6, 1e-2, log=True),
        #         random_state=seed,
        #     )
        if not trained:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
        score = r2_score(y_val, y_pred)
        scores.append(score)
        trial.report(float(np.mean(scores)), step=len(scores))
        if trial.should_prune():
            raise optuna.TrialPruned()
        #返回平均R方值
    return float(np.mean(scores))

def hyperparam_optimization(X, y, target_label, feature_index=None, n_trials=10):
    """
    仅做超参优化，不做特征选择，也不返回特征列表。
    feature_index: list[int] | list[str] | None
        指定使用的特征列索引或列名；None 表示使用全部特征。
    """
    model_names = ['GPR','LGBM','XGB','RFR','KNR','SVR']
    model_list = []
    results_list = []

    # 根据 feature_index 选取特征
    if feature_index is not None:
        X_selected = X.iloc[:, feature_index] if isinstance(feature_index[0], int) else X[feature_index]
    else:
        X_selected = X

    y_target = y[target_label]

    for model_name in model_names:
        seed = 42
        study = optuna.create_study(direction="maximize")
        study.optimize(
            lambda trial: objective(trial, model_name, X_selected, y_target),
            n_trials=n_trials,
            show_progress_bar=True
        )

        best_params = study.best_params
        best_score = study.best_value

        # 打印当前模型的最优结果
        print(f"[{model_name}] 最优 CV R2: {best_score:.4f}")
        print(f"         最优参数: {best_params}\n")

        if model_name == "Ridge":
            best_model = Ridge(random_state=seed, **best_params)
        elif model_name == "Lasso":
            best_model = Lasso(random_state=seed, **best_params)
        elif model_name == "RFR":
            best_model = RandomForestRegressor(n_jobs=-1, random_state=seed, **best_params)
        elif model_name == "LGBM":
            best_model = lgb.LGBMRegressor(random_state=seed,n_jobs=-1,**best_params)
        elif model_name == "DTR":
            # 决策树回归
            from sklearn.tree import DecisionTreeRegressor
            best_model = DecisionTreeRegressor(random_state=seed, **best_params)
        elif model_name == "ETR":
            # 极端随机树回归
            from sklearn.ensemble import ExtraTreesRegressor
            best_model = ExtraTreesRegressor(n_jobs=-1, random_state=seed, **best_params)
        elif model_name == "GBR":
            # 梯度提升回归
            from sklearn.ensemble import GradientBoostingRegressor
            best_model = GradientBoostingRegressor(random_state=seed, **best_params)
        elif model_name == "KNR":
            # K 近邻回归（无 random_state 参数）
            from sklearn.neighbors import KNeighborsRegressor
            best_model = KNeighborsRegressor(**best_params)
        elif model_name == "SVR":
            # 支持向量回归（无 random_state 参数）
            from sklearn.svm import SVR
            best_model = SVR(**best_params)
        elif model_name == "AdaBoost":
            from sklearn.ensemble import AdaBoostRegressor
            from sklearn.tree import DecisionTreeRegressor

            # 拷贝以免修改原 best_params
            bp = dict(best_params)

            # 取出弱学习器的参数（训练时你以 dt_* 命名）
            dt_kwargs = {}
            for key in ["dt_max_depth", "dt_min_samples_split", "dt_min_samples_leaf"]:
                if key in bp:
                    dt_kwargs[key.replace("dt_", "")] = bp.pop(key)

            # 构造弱学习器（注意 random_state）
            base_estimator = DecisionTreeRegressor(random_state=seed, **dt_kwargs)

            # 其余参数交给 AdaBoostRegressor（如 n_estimators, learning_rate, loss 等）
            best_model = AdaBoostRegressor(
                estimator=base_estimator,
                random_state=seed,
                **bp
            )
        elif model_name == "GPR":
            # 必要的 import（在文件头部也可全局导入）
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.gaussian_process.kernels import (
                RBF, Matern, RationalQuadratic,
                ConstantKernel as C, WhiteKernel
            )
            # 复制一份，避免修改原 best_params
            bp = dict(best_params)
            # 取 kernel 相关键（名字须与 objective 中一致）
            kernel_choice = bp.pop("kernel", "RBF")
            c = float(bp.pop("c", 1.0))
            noise = float(bp.pop("noise", 1e-6))
            ls_scalar = float(bp.pop("length_scale", 1.0))  # 在 objective 中若只搜了标量，则这里是标量基准
            matern_nu = bp.pop("matern_nu", bp.pop("nu",1.5))  # 兼容不同命名（优先 matern_nu）
            rq_alpha = float(bp.pop("rq_alpha", 1.0))
            rq_ls = float(bp.pop("rq_ls", 1.0))

            # 确定特征维度 p（用于 ARD 扩展）
            # 优先用 feature_index（训练时若保存了 feature_index 列表），否则尝试从 X_selected / X_train 等恢复
            if feature_index is not None and hasattr(feature_index, "__len__"):
                p = len(feature_index)
            elif "X_selected" in locals():
                p = X_selected.shape[1]
            else:
                p = None

            if p is not None:
                ls_eff = np.full(p, ls_scalar)
            else:
                ls_eff = ls_scalar

            # 构造 base kernel（bounds 设为合理范围，避免无限爆大）
            if kernel_choice == "RBF":
                base = RBF(length_scale=ls_eff, length_scale_bounds=(1e-2, 1e2))
            elif kernel_choice == "Matern":
                base = Matern(length_scale=ls_eff, length_scale_bounds=(1e-2, 1e2), nu=matern_nu)
            elif kernel_choice == "Matern+RQ":
                base = (Matern(length_scale=ls_eff, length_scale_bounds=(1e-2, 1e2), nu=matern_nu)
                        + RationalQuadratic(alpha=rq_alpha, length_scale=rq_ls))
            else:
                base = RBF(length_scale=ls_eff, length_scale_bounds=(1e-2, 1e2))

            kernel = C(c, (1e-3, 1e3)) * base + WhiteKernel(noise_level=noise,
                                                            noise_level_bounds=(1e-6, 1e0))

            # 1) 弹出 / 清理所有已知的 kernel 相关临时键，避免传给 GPR 构造器
            for k in ["kernel", "c", "noise", "length_scale", "ls_scalar", "ls_eff",
                      "ls_base", "matern_nu", "nu", "rq_alpha", "rq_ls", "ls_vector"]:
                bp.pop(k, None)

            # 2) 动态获取 GaussianProcessRegressor.__init__ 可接受的参数名（更兼容 sklearn 版本差异）
            gpr_init_params = set(inspect.signature(GaussianProcessRegressor.__init__).parameters.keys())
            gpr_init_params.discard("self")  # 去掉 self

            # 3) 只从 bp 中选择允许传入的那些键（其余全部丢弃）
            bp_filtered = {k: v for k, v in bp.items() if k in gpr_init_params}

            # 可选（调试）：打印被保留和被丢弃的键，便于排查
            # print("GPR keys kept:", bp_filtered.keys())
            # print("GPR keys dropped:", [k for k in bp.keys() if k not in bp_filtered])

            # 4) 最终构造模型（把 kernel 作为显式参数传入）
            best_model = GaussianProcessRegressor(
                kernel=kernel,
                random_state=seed,
                **bp_filtered
            )

        elif model_name == "XGB":
            # XGBoost 回归（需要 pip install xgboost）
            from xgboost import XGBRegressor
            best_model = XGBRegressor(n_jobs=-1, random_state=seed, **best_params)

        elif model_name == "ElasticNet":
            # 弹性网回归
            from sklearn.linear_model import ElasticNet
            best_model = ElasticNet(random_state=seed, **best_params)

        best_model.fit(X_selected, y_target)
        model_list.append(best_model)

        results_list.append({
            "Model": model_name,
            "Best Parameters": best_params,
            "Average Cross-Validation R2": best_score,
        })

    results_df = pd.DataFrame(results_list)
    # 现在（针对 R² 最大化）
    best_idx = results_df["Average Cross-Validation R2"].idxmax()
    best_model = model_list[best_idx]

    best_model_name = results_df.loc[best_idx, "Model"]
    best_cv_score = results_df.loc[best_idx, "Average Cross-Validation R2"]

    # 打印最终选中的模型及 CV 得分
    print(f"\n最终选择模型: {best_model_name}")
    print(f"对应平均 CV R2: {best_cv_score:.4f}\n")
    # 只返回结果表和最优模型
    return results_df, best_model,feature_index


def run_all_optimizations(targets, n_trials_list, X, y, feature_indices=None):
    """
    并行优化多个目标，支持为每个目标指定特征子集。
    feature_indices: list[list[int|str]|None] | None
        长度与 targets 一致；None 表示全部特征。
    """
    if feature_indices is None:
        feature_indices = [None] * len(targets)

    results = joblib.Parallel(n_jobs=1)(
        joblib.delayed(hyperparam_optimization)(
            X, y, target, feature_index=feat_idx, n_trials=n_trials
        )
        for target, n_trials, feat_idx in zip(targets, n_trials_list, feature_indices)
    )
    return results
def _call_metric(metric_item, y_true, y_pred):
    """
    统一调用指标：
    - callable: 直接 metric(y_true, y_pred)
    - (callable, dict): metric(y_true, y_pred, **kwargs)
    - (callable,): metric(y_true, y_pred)
    """
    # 1) 纯函数
    if callable(metric_item):
        return float(metric_item(y_true, y_pred))

    # 2) 元组
    if isinstance(metric_item, tuple):
        if len(metric_item) == 1 and callable(metric_item[0]):
            return float(metric_item[0](y_true, y_pred))
        if len(metric_item) == 2 and callable(metric_item[0]) and isinstance(metric_item[1], dict):
            func, kwargs = metric_item
            return float(func(y_true, y_pred, **kwargs))

    # 其他非法形式
    raise TypeError(
        "Metric must be a callable, (callable,), or (callable, kwargs_dict). "
        f"Got: {metric_item!r}"
    )

def evaluate_model(
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    metrics: Union[Callable, List[Union[Callable, tuple]]],
    metric_names: Union[str, List[str]]
) -> pd.DataFrame:
    # 统一成列表
    if not isinstance(metrics, list):
        metrics = [metrics]
    if not isinstance(metric_names, list):
        metric_names = [metric_names]

    if len(metrics) != len(metric_names):
        raise ValueError(f"`metrics` 与 `metric_names` 长度不一致: {len(metrics)} vs {len(metric_names)}")

    # 预测
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    # 计算指标（自动识别写法）
    train_scores = [_call_metric(m, y_train, y_train_pred) for m in metrics]
    test_scores  = [_call_metric(m, y_test,  y_test_pred)  for m in metrics]

    # 构建结果表
    df = pd.DataFrame(
        [train_scores, test_scores],
        index=["Train", "Test"],
        columns=metric_names
    )
    return df