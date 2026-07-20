# predict.py
import argparse
from pathlib import Path
from typing import List, Optional
import numpy as np
import pandas as pd
import joblib

# === 项目内工具 ===
from utils import preprocessing
def _find_latest_model_dir(base_dir: Path) -> Path:
    """
    自动查找 outputs 目录下最新的 model_ 开头的模型文件夹。
    例如：outputs/model_20251027_182130/
    """
    model_dirs = sorted(
        [d for d in base_dir.glob("model_*") if d.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    if not model_dirs:
        raise FileNotFoundError(f"在 {base_dir} 下未找到 model_ 开头的模型目录")
    latest = model_dirs[0]
    print(f"[INFO] 自动选择最新模型目录：{latest}")
    return latest
# ========== 1) 命令行参数 ==========
def parse_args():
    p = argparse.ArgumentParser(description="Predict HV for new HEA samples with trained pipeline.")
    p.add_argument("--model_dir", type=str, default="",
                   help="目录中应包含 Best_HV_pipeline.pkl（训练脚本已写出）")
    p.add_argument("--model_file", type=str, default="",
                   help="可选：直接指定模型文件（Best_HV_pipeline.pkl 或 Best_model_HV.pkl）")
    p.add_argument("--samples", type=str, default="./Data/New_HEA_samples.xlsx",
                   help="新样本成分表（列为元素，行和为1或可归一化）")
    p.add_argument("--elem_info", type=str, default="./Data/Element_info.csv",
                   help="训练期使用的元素物性表（与训练时一致）")
    p.add_argument("--enthalpy", type=str, default="./Data/Enthalpy_data.csv",
                   help="训练期使用的二元混合焓矩阵（与训练时一致）")
    p.add_argument("--sheet", type=str, default=None,
                   help="如果是Excel且需要指定sheet，可用此参数")
    p.add_argument("--out", type=str, default="Predicted_HV.xlsx",
                   help="输出预测结果Excel文件名")
    return p.parse_args()

# ========== 2) 实用函数 ==========
ID_COLS_GUESS = ["Alloys", "id", "ID", "sample", "Sample", "name", "Name"]  # 可选：随结果一起带出

def load_dataframe(path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"未找到文件：{p}")
    if p.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(p, sheet_name=sheet) if sheet else pd.read_excel(p)
    elif p.suffix.lower() in [".csv"]:
        return pd.read_csv(p)
    else:
        raise ValueError(f"不支持的文件类型：{p.suffix}")

def ensure_compositions(df: pd.DataFrame, elem_list: List[str]) -> pd.DataFrame:
    """
    只负责把元素成分列对齐到 elem_list 并做“行和=1”的归一化。
    不做任何 StandardScaler 的标准化；那一步由已保存的 Pipeline 内部完成。
    """
    # 1) 对齐列：缺失元素列补 0
    comp = df.reindex(columns=elem_list, fill_value=0.0).copy()

    # 2) 转为浮点 + 负数截断
    comp = comp.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    comp = comp.clip(lower=0.0)

    # 3) 若看起来是百分比（最大值明显 > 1），先转为 0~1 分数
    #   （阈值取 1.5，兼容少量浮点噪声）
    if comp.to_numpy().max() > 1.5:
        comp = comp / 100.0

    # 4) 行归一到 1（行和为 0 的，仍保持 0）
    row_sum = comp.sum(axis=1)
    row_sum_safe = row_sum.replace(0, np.nan)   # 避免除以 0
    comp = comp.div(row_sum_safe, axis=0).fillna(0.0)

    # 5) 再做一次极小数值修正，确保和为 1（行和为 0 的不用动）
    fix = comp.sum(axis=1).replace(0, 1.0)
    comp = comp.div(fix, axis=0)

    return comp[elem_list]

# ========== 3) 主流程 ==========
def main():
    args = parse_args()
    model_dir = Path(args.model_dir) if args.model_dir else _find_latest_model_dir(Path("./outputs"))
    model_pkl = Path(args.model_file) if args.model_file else (model_dir / "Best_HV_pipeline.pkl")
    if not model_pkl.exists():
        raise FileNotFoundError(f"未找到模型文件：{model_pkl}")

    # 3.1 加载模型与最终特征名
    model_obj = joblib.load(model_pkl)
    if isinstance(model_obj, dict) and "pipeline" in model_obj and "feature_names" in model_obj:
        pipe = model_obj["pipeline"]
        feature_names = model_obj["feature_names"]
    else:
        # 兼容 Best_model_HV.pkl：模型本体 + 从 Best_HV_pipeline.pkl 提取 feature_names
        pipe = model_obj
        art_path = model_dir / "Best_HV_pipeline.pkl"
        if not art_path.exists():
            raise FileNotFoundError(
                f"使用 Best_model_HV.pkl 时需要同目录存在 Best_HV_pipeline.pkl 以提供 feature_names：{art_path}"
            )
        art = joblib.load(art_path)
        if not isinstance(art, dict) or "feature_names" not in art:
            raise ValueError("Best_HV_pipeline.pkl 中未找到 feature_names")
        feature_names = art["feature_names"]
    print(f"[INFO] 模型加载成功：{model_pkl}")
    print(f"[INFO] 训练期最终特征数 = {len(feature_names)}")

    # 3.2 读入新样本、元素物性、二元混合焓
    df_new = load_dataframe(args.samples, args.sheet)
    elem_info = load_dataframe(args.elem_info)
    enthalpy  = load_dataframe(args.enthalpy)

    # Use the same element list as the training pipeline.
    elem_list = ['Al','Co','Cr','Cu','Fe','Hf','Mn','Mo','Nb','Ni','Ta','Ti','V','W','Zr']

    # 把二表对齐到 elem_list
    enthalpy = enthalpy.set_index("Elements")[elem_list].loc[elem_list]
    elem_info = elem_info.set_index("Symbol").loc[elem_list].drop(columns="Symbol", errors="ignore")

    # Keep derived input columns aligned with the training pipeline.
    if "XSv" not in elem_info.columns and all(c in elem_info.columns for c in ["VEC", "ENp"]):
        # 示例：elem_info['XSv'] = np.dot(elem_info['VEC'], elem_info['ENp'])  # 你训练时的写法
        # 更严谨写法（逐元素相乘）：与训练脚本保持同一实现
        elem_info["XSv"] = elem_info["VEC"] * elem_info["ENp"]

    # 3.4 取ID列（可选）
    id_cols = [c for c in df_new.columns if c in ID_COLS_GUESS]
    id_frame = df_new[id_cols].copy() if id_cols else pd.DataFrame(index=df_new.index)

    # 3.5 提取并归一化成分
    comp = ensure_compositions(df_new, elem_list)

    # 3.6 用训练时完全一致的逻辑构建特征池
    # Match train.py: generate_features + Hmix + Smix + drop elements + fillna.
    H_data = enthalpy.values
    phys_data = elem_info.values
    phys_names = elem_info.columns.tolist()

    feat_pool = preprocessing.generate_features(
        comp.values, phys_data, elem_list, phys_names
    )
    feat_pool["Hmix"] = preprocessing.calculate_H_mix(comp, H_data)
    feat_pool["Smix"] = preprocessing.entropy(comp)
    feat_pool = feat_pool.drop(columns=elem_list, errors="ignore")
    feat_pool = feat_pool.fillna(0)

    # 3.7 严格对齐训练期最终特征名（顺序必须一致；缺失列报错提示）
    missing = [c for c in feature_names if c not in feat_pool.columns]
    if missing:
        raise ValueError(
            f"新数据缺少训练期的关键特征 {len(missing)} 个：{missing[:10]} ...\n"
            f"请检查 Element_info.csv / Enthalpy_data.csv 是否与训练时一致，以及派生特征是否按相同逻辑生成。"
        )
    X_pred = feat_pool[feature_names].copy()

    # 3.8 预测：管道内已包含 MinMaxScaler，因此无需再缩放
    y_pred_log = pipe.predict(X_pred)  # The training target uses log1p(HV).
    y_pred = np.expm1(y_pred_log)

    # 3.9 组织并保存结果
    out_df = id_frame.copy()
    out_df["Pred_HV"] = y_pred
    out_path = Path(args.out)
    out_df.to_excel(out_path, index=False)
    print(f"[OK] 预测完成：{len(out_df)} 条样本，结果已保存 -> {out_path.resolve()}")

if __name__ == "__main__":
    main()
