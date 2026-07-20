# backend/predictions/hv_service.py
"""
封装 HV-Prediction 模块：根据成分预测硬度 HV。
依赖项目根目录下的 HV-Prediction（含 outputs/、Data/、utils/）。
"""
import sys
import os
from pathlib import Path
import json
import subprocess
import tempfile
from typing import Any, Dict, List
import pandas as pd

# 项目根目录（backend 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
HV_ROOT = BASE_DIR / "HV-Prediction"
FIXED_MODEL_DIR = HV_ROOT / "outputs" / "model_20260320_062441"
FIXED_MODEL_PKL = FIXED_MODEL_DIR / "Best_HV_pipeline.pkl"
ELEM_LIST = [
    'Al', 'Co', 'Cr', 'Cu', 'Fe', 'Hf', 'Mn', 'Mo',
    'Nb', 'Ni', 'Ta', 'Ti', 'V', 'W', 'Zr'
]


def _normalize_like_predict(composition: dict) -> Dict[str, float]:
    """
    与 HV-Prediction/predict.py 的 ensure_compositions 单样本逻辑一致。
    """
    # 1) 对齐列（缺失补 0）
    comp = pd.DataFrame([{e: composition.get(e, 0.0) for e in ELEM_LIST}]).reindex(
        columns=ELEM_LIST, fill_value=0.0
    )
    # 2) to_numeric + fillna(0) + clip(lower=0)
    comp = comp.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    comp = comp.clip(lower=0.0)
    # 3) 百分比判定（max > 1.5）
    if comp.to_numpy().max() > 1.5:
        comp = comp / 100.0
    # 4) 行归一（sum=0 保持 0）
    row_sum = comp.sum(axis=1)
    row_sum_safe = row_sum.replace(0, float("nan"))
    comp = comp.div(row_sum_safe, axis=0).fillna(0.0)
    # 5) 二次修正（与 predict.py 完全一致）
    fix = comp.sum(axis=1).replace(0, 1.0)
    comp = comp.div(fix, axis=0)
    row = comp.iloc[0].to_dict()
    return {e: float(row[e]) for e in ELEM_LIST}


def _batch_rows_from_samples(samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将 API 中的多条样本转为与 Excel 批量脚本一致的行（元素列 + 其它列如 Alloys）。"""
    rows = []
    for s in samples:
        row: Dict[str, Any] = {e: float(s.get(e, 0) or 0) for e in ELEM_LIST}
        for k, v in s.items():
            if k not in ELEM_LIST:
                row[k] = v
        rows.append(row)
    return rows


def predict_hv_batch(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量预测：一次写入多行 samples.xlsx，单次调用 predict.py。
    与你在命令行对整表批量运行 predict.py 的特征工程行为一致（含 F* 跨行依赖）。
    """
    if not samples:
        raise ValueError("samples 不能为空")
    if len(samples) > 500:
        raise ValueError("单次批量最多 500 条")

    model_pkl = FIXED_MODEL_PKL
    if not model_pkl.exists():
        raise FileNotFoundError(f"未找到指定模型文件: {model_pkl}")
    script = HV_ROOT / "predict.py"
    if not script.exists():
        raise FileNotFoundError(f"未找到预测入口脚本: {script}")

    python_exe = sys.executable

    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    env.setdefault("NUMEXPR_NUM_THREADS", "1")
    env.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    env.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

    elem_info = HV_ROOT / "Data" / "Element_info.csv"
    enthalpy = HV_ROOT / "Data" / "Enthalpy_data.csv"
    if not elem_info.exists():
        raise FileNotFoundError(f"未找到元素物性文件: {elem_info}")
    if not enthalpy.exists():
        raise FileNotFoundError(f"未找到混合焓文件: {enthalpy}")

    rows = _batch_rows_from_samples(samples)
    df_in = pd.DataFrame(rows)
    extra = [c for c in df_in.columns if c not in ELEM_LIST]
    df_in = df_in[extra + [e for e in ELEM_LIST if e in df_in.columns]]

    # Use the operating-system temp directory so a read-only checkout can serve predictions.
    with tempfile.TemporaryDirectory(prefix="nuheamine_hv_batch_") as tmp_dir:
        tmp = Path(tmp_dir)
        samples_path = tmp / "samples.xlsx"
        out_path = tmp / "pred.xlsx"

        df_in.to_excel(samples_path, index=False)

        cmd = [
            str(python_exe), str(script),
            "--model_dir", str(FIXED_MODEL_DIR),
            "--model_file", str(model_pkl),
            "--samples", str(samples_path),
            "--elem_info", str(elem_info),
            "--enthalpy", str(enthalpy),
            "--out", str(out_path),
        ]
        timeout_sec = max(300, 60 + 30 * len(samples))
        try:
            cp = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                cwd=str(HV_ROOT),
                env=env,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"批量预测超时（{timeout_sec}s）")

        if cp.returncode != 0:
            msg = (cp.stderr or cp.stdout or "").strip()
            raise RuntimeError(f"HV-Prediction 子进程执行失败（code={cp.returncode}）：{msg}")

        if not out_path.exists():
            raise RuntimeError(f"预测结果文件未生成: {out_path}")

        try:
            pred_df = pd.read_excel(out_path)
            if "Pred_HV" not in pred_df.columns or pred_df.empty:
                raise RuntimeError("预测结果缺少 Pred_HV")
        except Exception as e:
            raise RuntimeError(f"解析预测结果失败: {e}")

    records = json.loads(pred_df.to_json(orient="records", date_format="iso"))

    return {
        "results": records,
        "batch_size": len(records),
    }


def predict_hv(composition: dict) -> Dict[str, Any]:
    """
    通过调用 HV-Prediction 的预测入口脚本进行预测（子进程隔离）。

    - 不在 Django 进程内加载模型/依赖，避免 native crash 直接带走后端
    - 最大程度复用你在 HV-Prediction 中封装好的预测逻辑与模型文件
    """
    # 切回使用完整工件 Best_HV_pipeline.pkl（更稳妥，和训练/脚本流程最一致）
    model_pkl = FIXED_MODEL_PKL
    if not model_pkl.exists():
        raise FileNotFoundError(f"未找到指定模型文件: {model_pkl}")
    script = HV_ROOT / "predict.py"
    if not script.exists():
        raise FileNotFoundError(f"未找到预测入口脚本: {script}")

    # 强制与 Django 主进程使用同一 Python 环境
    python_exe = sys.executable

    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    env.setdefault("NUMEXPR_NUM_THREADS", "1")
    env.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    env.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

    # 与你单独预测保持一致：调用 HV-Prediction/predict.py，
    # 通过临时 samples.xlsx -> out.xlsx 的方式获取 Pred_HV
    elem_info = HV_ROOT / "Data" / "Element_info.csv"
    enthalpy = HV_ROOT / "Data" / "Enthalpy_data.csv"
    if not elem_info.exists():
        raise FileNotFoundError(f"未找到元素物性文件: {elem_info}")
    if not enthalpy.exists():
        raise FileNotFoundError(f"未找到混合焓文件: {enthalpy}")

    # Use the operating-system temp directory so a read-only checkout can serve predictions.
    with tempfile.TemporaryDirectory(prefix="nuheamine_hv_") as tmp_dir:
        tmp = Path(tmp_dir)
        samples_path = tmp / "samples.xlsx"
        out_path = tmp / "pred.xlsx"

        row = {e: float(composition.get(e, 0) or 0) for e in ELEM_LIST}
        pd.DataFrame([row]).to_excel(samples_path, index=False)
        normalized = _normalize_like_predict(composition)

        cmd = [
            str(python_exe), str(script),
            "--model_dir", str(FIXED_MODEL_DIR),
            "--model_file", str(model_pkl),
            "--samples", str(samples_path),
            "--elem_info", str(elem_info),
            "--enthalpy", str(enthalpy),
            "--out", str(out_path),
        ]
        try:
            cp = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                cwd=str(HV_ROOT),
                env=env,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise TimeoutError("预测超时（120s）")

        if cp.returncode != 0:
            msg = (cp.stderr or cp.stdout or "").strip()
            raise RuntimeError(f"HV-Prediction 子进程执行失败（code={cp.returncode}）：{msg}")

        if not out_path.exists():
            raise RuntimeError(f"预测结果文件未生成: {out_path}")

        try:
            pred_df = pd.read_excel(out_path)
            if "Pred_HV" not in pred_df.columns or pred_df.empty:
                raise RuntimeError("预测结果缺少 Pred_HV")
            pred_hv = float(pred_df.iloc[0]["Pred_HV"])
        except Exception as e:
            raise RuntimeError(f"解析预测结果失败: {e}")

    return {
        "Pred_HV": pred_hv,
        "normalized_composition": normalized,
    }
