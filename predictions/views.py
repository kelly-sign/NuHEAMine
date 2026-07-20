# 统一从 backend.predictions 导出，供 backend.urls 使用
from backend.predictions.views import (
    hv_predict,
    hv_predict_batch,
    prediction_under_development,
    prediction_history_list,
    prediction_history_detail,
)

__all__ = [
    'hv_predict',
    'hv_predict_batch',
    'prediction_under_development',
    'prediction_history_list',
    'prediction_history_detail',
]
