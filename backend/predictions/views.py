from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import connection
from django.utils import timezone
import json
import logging
from predictions.models import PredictionRecord
from .serializers import (
    HVPredictionInputSerializer,
    HVPredictionBatchInputSerializer,
    HV_ELEMENTS,
)
from .hv_service import predict_hv, predict_hv_batch


logger = logging.getLogger(__name__)
_PRED_TABLE_COLS = None


def _prediction_table_name() -> str:
    return PredictionRecord._meta.db_table


def _get_table_columns() -> set:
    global _PRED_TABLE_COLS
    if _PRED_TABLE_COLS is not None:
        return _PRED_TABLE_COLS
    table = _prediction_table_name()
    with connection.cursor() as cur:
        cur.execute(f"SHOW COLUMNS FROM `{table}`")
        cols = {row[0] for row in cur.fetchall()}
    _PRED_TABLE_COLS = cols
    return cols


def _row_to_record_dict(row: dict, username: str) -> dict:
    # 兼容 JSONField 取回为 str 的情况
    def _maybe_json(x):
        if isinstance(x, (dict, list)) or x is None:
            return x
        if isinstance(x, (bytes, bytearray)):
            x = x.decode("utf-8", errors="ignore")
        if isinstance(x, str):
            try:
                return json.loads(x)
            except Exception:
                return x
        return x

    return {
        "id": row.get("id"),
        "prediction_type": row.get("prediction_type", "hv"),
        "input_data": _maybe_json(row.get("input_data")) or {},
        "output_data": _maybe_json(row.get("output_data")) or {},
        "created_by": username,
        "created_by_id": row.get("created_by_id"),
        "created_at": row.get("created_at"),
        "model_name": "HV Hardness Prediction",
    }

def _user_fk_col(cols: set) -> str:
    if "created_by_id" in cols:
        return "created_by_id"
    if "created_by" in cols:
        return "created_by"
    raise RuntimeError("The prediction_records table is missing a user field (created_by_id/created_by).")


def _insert_prediction_record(*, user_id: int, composition: dict, pred_hv: float) -> dict:
    table = _prediction_table_name()
    cols = _get_table_columns()
    user_col = _user_fk_col(cols)

    # 按项目配置时区（Asia/Shanghai）转换后写入数据库
    now = timezone.localtime(timezone.now()).replace(tzinfo=None)
    input_data = {"composition": composition}
    output_data = {"Pred_HV": pred_hv}

    fields = []
    values = []
    params = []

    def add(col, val):
        fields.append(f"`{col}`")
        values.append("%s")
        params.append(val)

    if "prediction_type" in cols:
        add("prediction_type", "hv")
    if "input_data" in cols:
        add("input_data", json.dumps(input_data, ensure_ascii=False))
    if "output_data" in cols:
        add("output_data", json.dumps(output_data, ensure_ascii=False))
    add(user_col, user_id)
    if "created_at" in cols:
        add("created_at", now)

    if not fields:
        raise RuntimeError(f"The prediction history table `{table}` has no writable fields; check its schema.")

    sql = f"INSERT INTO `{table}` ({', '.join(fields)}) VALUES ({', '.join(values)})"
    with connection.cursor() as cur:
        cur.execute(sql, params)
        new_id = cur.lastrowid

    return {
        "id": new_id,
        "prediction_type": "hv",
        "input_data": input_data,
        "output_data": output_data,
        "created_by_id": user_id,
        "created_at": now,
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prediction_under_development(_request):
    """Stable API placeholder for prediction models that are not deployed yet."""
    return Response(
        {
            'code': 200,
            'status': 'developing',
            'message': 'Prediction model is under development',
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hv_predict(request):
    """HV 硬度预测：前端传入 15 种元素成分，返回 Pred_HV 并写入预测记录。"""
    serializer = HVPredictionInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    composition = serializer.validated_data['composition']
    try:
        pred = predict_hv(composition)
        pred_hv = float(pred["Pred_HV"])
    except FileNotFoundError:
        logger.exception("The hardness model or one of its data files is missing.")
        return Response(
            {'error': 'The hardness prediction service is unavailable.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        logger.exception("Hardness prediction failed.")
        return Response(
            {'error': 'Hardness prediction failed.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    try:
        row = _insert_prediction_record(
            user_id=request.user.pk,
            composition=composition,
            pred_hv=pred_hv
        )
        return Response(
            _row_to_record_dict(row, request.user.username),
            status=status.HTTP_201_CREATED
        )
    except Exception:
        logger.exception("Prediction succeeded, but saving its history failed.")
        return Response(
            {'error': 'Prediction succeeded, but saving the history failed.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def hv_predict_batch(request):
    """
    批量 HV 硬度预测：一次请求内多行成分，单次调用 predict.py，与命令行整表批量预测一致。
    可选 save_history=true 时为每条写入一条预测历史（默认 false，不改变历史表写入习惯）。
    """
    serializer = HVPredictionBatchInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    samples = serializer.validated_data['samples']
    save_history = serializer.validated_data.get('save_history', False)
    try:
        pred = predict_hv_batch(samples)
    except FileNotFoundError:
        logger.exception("The hardness model or one of its data files is missing.")
        return Response(
            {'error': 'The hardness prediction service is unavailable.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception("Batch hardness prediction failed.")
        return Response(
            {'error': 'Batch hardness prediction failed.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    results = pred.get('results') or []
    response_body = {
        'results': results,
        'batch_size': pred.get('batch_size', len(results)),
    }

    if save_history:
        saved = []
        errors = []
        for i, row in enumerate(results):
            try:
                comp = {e: float(samples[i].get(e, 0) or 0) for e in HV_ELEMENTS}
                phv = row.get('Pred_HV')
                if phv is None:
                    errors.append(f'Item {i + 1} is missing Pred_HV.')
                    continue
                rec = _insert_prediction_record(
                    user_id=request.user.pk,
                    composition=comp,
                    pred_hv=float(phv),
                )
                saved.append(_row_to_record_dict(rec, request.user.username))
            except Exception:
                logger.exception("Failed to save batch prediction item %s.", i + 1)
                errors.append(f'Failed to save item {i + 1}.')
        response_body['saved_records'] = saved
        response_body['save_errors'] = errors
        if errors and not saved:
            return Response(
                {
                    'error': 'Batch prediction succeeded, but all history records failed to save.',
                    'detail': errors,
                    'results': response_body['results'],
                    'batch_size': response_body['batch_size'],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(response_body, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prediction_history_list(request):
    """当前用户的预测历史（HV）。"""
    table = _prediction_table_name()
    cols = _get_table_columns()
    user_col = _user_fk_col(cols)
    order_col = "created_at" if "created_at" in cols else "id"
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT * FROM `{table}` WHERE `{user_col}`=%s ORDER BY `{order_col}` DESC",
            [request.user.pk]
        )
        columns = [c[0] for c in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    return Response([_row_to_record_dict(r, request.user.username) for r in rows])


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def prediction_history_detail(request, pk):
    """单条预测记录详情或删除。"""
    table = _prediction_table_name()
    cols = _get_table_columns()
    user_col = _user_fk_col(cols)

    with connection.cursor() as cur:
        cur.execute(
            f"SELECT * FROM `{table}` WHERE `id`=%s AND `{user_col}`=%s LIMIT 1",
            [pk, request.user.pk]
        )
        row = cur.fetchone()
        if not row:
            return Response(status=status.HTTP_404_NOT_FOUND)
        columns = [c[0] for c in cur.description]
        row_dict = dict(zip(columns, row))

    if request.method == 'GET':
        return Response(_row_to_record_dict(row_dict, request.user.username))

    with connection.cursor() as cur:
        cur.execute(
            f"DELETE FROM `{table}` WHERE `id`=%s AND `{user_col}`=%s",
            [pk, request.user.pk]
        )
        if cur.rowcount == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)
