import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
import warnings
warnings.filterwarnings('ignore')
import joblib
import tempfile
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import xgboost as xgb
from utils import (
    feature_selection,
    preprocessing,
    detect_anomality,
    model,
    sampling)
from sklearn.model_selection import (
    train_test_split,
    KFold
)
from sklearn.pipeline import (
    make_pipeline,
    Pipeline)
from sklearn.preprocessing import (
    MinMaxScaler,
    StandardScaler,
    RobustScaler)
from sklearn.linear_model import LassoCV, Lasso
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error)
from utils.model import rmse  # 确保能导入到 rmse
from typing import List
def log3sigma_filter(df: pd.DataFrame,
                     col: str = 'HV',
                     sigma: float = 3.0,
                     reset_index: bool = True) -> pd.DataFrame:
    """
    对指定列做对数变换后，按 3σ 原则剔除离群点。

    参数
    ----
    df : pd.DataFrame
        原始数据框
    col : str
        待处理的列名，默认 'HV'
    sigma : float
        标准差倍数阈值，默认 3.0
    reset_index : bool
        是否重置索引，默认 True

    返回
    ----
    pd.DataFrame
        剔除离群点后的数据框
    """

    # 1. 对数变换（加极小值防止 log(0)）
    log_vals = np.log10(df[col] + np.finfo(float).eps)

    # 2. 计算 z-score
    z = (log_vals - log_vals.mean()) / log_vals.std()

    # 3. 过滤
    mask = np.abs(z) < sigma
    df_clean = df.loc[mask]

    # 4. 可选：重置索引
    if reset_index:
        df_clean = df_clean.reset_index(drop=True)

    return df_clean

def normalize_composition(df: pd.DataFrame,
                          cols: List[str],
                          decimals: int = 2) -> pd.DataFrame:
    """
    归一化 → round → 误差二次修正，确保每行和严格为 1。
    原地修改 df，返回同一对象。
    """
    # 1. 归一化
    row_sum = df[cols].sum(axis=1)
    if (row_sum <= 0).any():
        raise ValueError("存在行和≤0，无法归一化。")

    df[cols] = df[cols].div(row_sum, axis=0).round(decimals)

    # 2. 计算残差
    residual = 1.0 - df[cols].sum(axis=1)

    # 3. 逐行修正
    for idx, delta in residual.items():
        if abs(delta) < 1e-12:
            continue  # 已满足

        # 找到绝对值最大的分量，把残差加给它
        c = cols[np.argmax(np.abs(df.loc[idx, cols]))]
        df.at[idx, c] += delta
        # 保证非负
        if df.at[idx, c] < 0:
            raise ValueError(f"修正后出现负值，行 {idx}，列 {c}")

    # 4. 最终校验
    assert (df[cols].sum(axis=1).round(10) == 1.0).all(), "修正失败"
    return df

rand_seed = 42
np.random.seed(rand_seed)

raw_data = pd.read_excel("./Data/HV-Data.xlsx")
raw_data = raw_data.iloc[:, 1:]   # 保留从第 2 列开始的数据
elem_list = ['Al','Co','Cr','Cu','Fe','Hf','Mn','Mo','Nb','Ni','Ta','Ti','V','W','Zr']
tgt_cols = ["HV"]
result = detect_anomality.detect_feature_label_anomalies(
    df=raw_data,
    feature_columns=elem_list,
    label_column='HV',
    n_neighbors=5,
    threshold=4.5
)
df1 = raw_data.drop(index=result['anomaly_indices'])
print(f"\n检测到 {result['anomaly_count']} 个异常点")
print("异常点索引:", result['anomaly_indices'])

# 显示统计信息
print(f"\n统计信息:")
print(f"总样本数: {result['total_samples']}")
print(f"异常点比例: {result['anomaly_ratio']:.3f}")
print("result字典中的所有键：", result.keys())
# 替换原打印语句，使用已存在的稳健性指标
print(f"稳健中位数平均相对变化: {result['robust_median_avg_relative_change']:.3f}")
print(f"稳健MAD平均相对变化: {result['robust_mad_avg_relative_change']:.3f}")
print(f"使用的阈值: {result['threshold_used']} 倍标准差")

# 显示详细的异常点信息
if result['anomaly_count'] > 0:
    print("\n异常点详细信息:")
    for idx in result['anomaly_indices']:
        info = next(item for item in result['anomalies_info'] if item['index'] == idx)
        print(f"索引 {idx}: 标签值={info['label_value']:.2f}, "
            f"平均相对变化={info['avg_relative_change']:.2f}, "
            f"最大相对变化={info['max_relative_change']:.2f}")
        
data_cleaned_1st_step = raw_data.drop(index=result['anomaly_indices'])
data_cleaned_final = log3sigma_filter(data_cleaned_1st_step,col='HV',sigma=2.0,reset_index=True)
print(f"原始行数: {len(raw_data)}, 异常检测后: {len(df1)}, 剔除离群点过滤后行数: {len(data_cleaned_final)}")
comp_data = normalize_composition(data_cleaned_final,elem_list,decimals=2)[elem_list].round(2)
tgt_data = data_cleaned_final[tgt_cols]

# Assume logarithmic Gaussian distribution
lg_hv = np.log1p(tgt_data['HV'].values)
# 包装成 DataFrame，并保持和原来一样的格式
tgt_data_proc = pd.DataFrame(lg_hv, columns=tgt_cols)
# Load physical properties
enthalpy_data = pd.read_csv("./Data/Enthalpy_data.csv")
enthalpy_data.index = enthalpy_data["Elements"]
element_info = pd.read_csv("./Data/Element_info.csv")
element_info.index = element_info["Symbol"]
H_data = enthalpy_data[elem_list].loc[elem_list].values
elem_data = element_info.loc[elem_list]
elem_data = elem_data.drop(columns="Symbol")

# Revised at Jul 29 2025
# Reference: Luo, Z., Gao, W., & Jiang, Q. (2025). Determinants of vacancy formation and migration in high-entropy alloys. Science Advances, 11(1), 1–10. https://doi.org/10.1126/sciadv.adr4697
elem_data['XSv'] = np.dot(elem_data['VEC'],elem_data['ENp']) 

# Generate feature pool
feature_pool_init = preprocessing.generate_features(
    comp_data.values, elem_data.values, elem_list, elem_data.columns
)

# Add supplementary features
feature_pool_init["Hmix"] = preprocessing.calculate_H_mix(comp_data, H_data)
feature_pool_init["Smix"] = preprocessing.entropy(comp_data) 
feature_pool_init = feature_pool_init.drop(columns=elem_list)
feature_pool_init = feature_pool_init.fillna(0)
print(f"原始特征数: {feature_pool_init.shape[1]}")
print(f"原始特征名称: {list(feature_pool_init.columns)}")
X_train,X_test,y_train,y_test = train_test_split(
    feature_pool_init,tgt_data_proc,test_size=0.3,random_state=rand_seed)

X_train_scaled = preprocessing.normalize_features(X_train,X_train,MinMaxScaler())
X_test_scaled  = preprocessing.normalize_features(X_train,X_test,MinMaxScaler())
y_train_scaled = preprocessing.normalize_features(y_train,y_train,MinMaxScaler())
y_test_scaled  = preprocessing.normalize_features(y_train,y_test,MinMaxScaler())

# 1) 针对单目标 HV 做特征筛选（与原先 Di/Dv/Div 流程等价）
cols_hv = feature_selection.feature_selection_pipeline(
    X_train_scaled,          # 与原来 Di 一样，用 scaled 的特征做筛选
    y_train['HV'],           # 目标改为 HV
    task='regression',
    corr_ratio=0.8,
    corr_threshold=0.9,
    max_features=20,
    cache_dir=None
)
print("=== 过滤法粗筛（方差+相关性）,特征筛选结果 ===")
print(f"筛选后特征数: {len(cols_hv)}")
print(f"筛选后特征: {cols_hv}")
# 第二阶段：LASSO 二次精炼（防过拟合版）
lasso_info = feature_selection.lasso_refine_features(
    X=X_train,                 # 注意：这里用“未缩放”的 X_train
    y=y_train["HV"],
    base_features=cols_hv,
    max_keep=12,               # 可调：8~15
    cv=10,                     # 可调：5~10
    random_state=rand_seed,
    alpha_multiplier=1.5       # 可调：1.2~2.0 越大越保守
)
feature_hv = lasso_info["features"]
print("=== LASSO二次精炼精筛,特征筛选结果 ===")
print(f"alpha_best={lasso_info['alpha_best']:.4g}, alpha_used={lasso_info['alpha_used']:.4g}")
print(f"筛选后特征数: {len(feature_hv)}")
print(f"筛选后特征: {feature_hv}")

# 3) 把最终特征名单传给优化器（targets / n_trials_list / feature_indices 均为单元素列表）
all_results = model.run_all_optimizations(
    targets=["HV"],
    n_trials_list=[100],
    X=X_train_scaled,        # 与筛选阶段一致，传 scaled 特征矩阵
    y=y_train,
    feature_indices=[feature_hv],
)
base_results_df_HV, base_best_model_HV, _ = all_results[0]  # 仅参考，不往下用
#在此处追加单独针对表现好的模型高 trial 优化
results_df_HV, best_model_HV, feature_hv = model.hyperparam_optimization(
    X=X_train_scaled,
    y=y_train,
    target_label="HV",
    feature_index=feature_hv,
    n_trials=200,   # 或更大
)
model_metrics_hv = model.evaluate_model(
    model=best_model_HV,
    X_train=X_train_scaled[feature_hv],   # 与前面传给优化器一致：用 scaled 特征
    y_train=y_train["HV"],
    X_test=X_test_scaled[feature_hv],
    y_test=y_test["HV"],
    metrics = [r2_score,mean_absolute_error,rmse,mean_absolute_percentage_error],
    metric_names=["R2","MAE","RMSE","MAPE"]
)
y_train_lin = np.expm1(y_train["HV"]).to_numpy()
y_test_lin  = np.expm1(y_test["HV"]).to_numpy()
y_pred_train_lin = np.expm1(best_model_HV.predict(X_train_scaled[feature_hv]))
y_pred_test_lin  = np.expm1(best_model_HV.predict(X_test_scaled[feature_hv]))
print("\n=== 原 HV 空间评估 ===")
print(f"Train R2 : {r2_score(y_train_lin, y_pred_train_lin):.4f}")
print(f"Test  R2 : {r2_score(y_test_lin,  y_pred_test_lin):.4f}")
print(f"Test MAE : {mean_absolute_error(y_test_lin, y_pred_test_lin):.4f}")
print(f"Test RMSE: {rmse(y_test_lin, y_pred_test_lin):.4f}")
print(f"Test MAPE: {mean_absolute_percentage_error(y_test_lin, y_pred_test_lin):.4f}")
# === 将原始 HV 空间指标写入 Excel（两行：Train / Test） ===
df_metrics_hv_linear = pd.DataFrame(
    [
        [
            r2_score(y_train_lin, y_pred_train_lin),
            mean_absolute_error(y_train_lin, y_pred_train_lin),
            rmse(y_train_lin, y_pred_train_lin),
            mean_absolute_percentage_error(y_train_lin, y_pred_train_lin),
        ],
        [
            r2_score(y_test_lin, y_pred_test_lin),
            mean_absolute_error(y_test_lin, y_pred_test_lin),
            rmse(y_test_lin, y_pred_test_lin),
            mean_absolute_percentage_error(y_test_lin, y_pred_test_lin),
        ],
    ],
    columns=["R2","MAE","RMSE","MAPE"],
    index=["Train", "Test"],
)

# --- 3) 汇总特征索引（保持原有 DataFrame 结构，只是单行）---
feature_indices = pd.DataFrame([feature_hv], index=['HV'])
# print(feature_indices)
# -------------------------------------------------
# 1. 生成以时间戳命名的安全输出目录
# -------------------------------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
safe_root = Path("./outputs") / f"model_{timestamp}"
safe_root.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# 2. 定义统一的保存函数，带异常兜底
# -------------------------------------------------
def safe_save_df(df: pd.DataFrame, stem: str):
    """把 DataFrame 存成 Excel，失败时写到临时目录"""
    try:
        df.to_excel(safe_root / f"{stem}.xlsx", index=False)
    except PermissionError as e:
        # 降级到系统临时目录
        with tempfile.TemporaryDirectory() as tmp:
            fallback = Path(tmp) / f"{stem}.xlsx"
            df.to_excel(fallback, index=False)
            print(f"[WARN] 无法写入 {safe_root}，已临时保存到 {fallback}：{e}")

def safe_save_model(model, stem: str):
    """保存模型，失败时写到临时目录"""
    try:
        joblib.dump(model, safe_root / f"{stem}.pkl")
    except PermissionError as e:
        with tempfile.TemporaryDirectory() as tmp:
            fallback = Path(tmp) / f"{stem}.pkl"
            joblib.dump(model, fallback)
            print(f"[WARN] 无法写入 {safe_root}，已临时保存到 {fallback}：{e}")

# --- 保存单目标 HV 的优化结果和评估结果 ---
safe_save_df(results_df_HV, "HyperParamOpt-HV")

safe_save_df(model_metrics_hv, "model_metric_HV")

safe_save_df(df_metrics_hv_linear, "model_metric_HV_linear")

safe_save_df(feature_indices, "features")

feature_summary = pd.DataFrame({
    "阶段": ["原始特征", "粗筛后特征", "精筛后特征"],
    "特征数": [feature_pool_init.shape[1], len(cols_hv), len(feature_hv)],
    "特征列表": [", ".join(feature_pool_init.columns), ", ".join(cols_hv), ", ".join(feature_hv)]
})
feature_summary.to_excel("feature_summary_HV.xlsx", index=False)
# --- 保存最佳模型 ---
safe_save_model(best_model_HV, "Best_model_HV")

print(f"所有文件已写入：{safe_root.resolve()}")

# 构建包含标准化的完整管道
pipe_HV = make_pipeline(MinMaxScaler(), best_model_HV)
pipe_HV.fit(X_train[feature_hv], y_train['HV'])

# 保存管道、特征名及划分索引\
joblib.dump({
    "pipeline": pipe_HV,
    "feature_names": feature_hv,
    "train_index": X_train.index.to_list(),
    "test_index":  X_test.index.to_list()
}, safe_root / "Best_HV_pipeline.pkl")
