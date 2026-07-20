from rest_framework import serializers
from predictions.models import PredictionRecord

# HV 预测使用的 15 种元素（与 HV-Prediction 一致）
HV_ELEMENTS = [
    'Al', 'Co', 'Cr', 'Cu', 'Fe', 'Hf', 'Mn', 'Mo',
    'Nb', 'Ni', 'Ta', 'Ti', 'V', 'W', 'Zr'
]


class HVPredictionInputSerializer(serializers.Serializer):
    """HV 硬度预测：15 种元素成分，可为百分比(0~100)或原子分数(0~1)。"""
    composition = serializers.DictField(
        child=serializers.FloatField(min_value=0, max_value=100)
    )

    def validate_composition(self, value):
        unknown_elements = sorted(set(value) - set(HV_ELEMENTS))
        if unknown_elements:
            raise serializers.ValidationError(
                f"Unsupported element(s): {', '.join(unknown_elements)}."
            )

        total = sum(value.get(element, 0) for element in HV_ELEMENTS)
        if total <= 0:
            raise serializers.ValidationError(
                "The total of the supported element compositions must be greater than 0."
            )
        # 允许 0~1 或 0~100，后端会归一化
        return value


class HVPredictionBatchInputSerializer(serializers.Serializer):
    """
    批量 HV 预测：与整表运行 predict.py 一致（单次子进程、同一批样本矩阵）。
    每条为 dict：必须含 15 元素键（可省略，视为 0）；可含 Alloys / name 等非元素字段。
    """
    samples = serializers.ListField(
        child=serializers.JSONField(),
        min_length=1,
        max_length=500,
    )
    save_history = serializers.BooleanField(required=False, default=False)

    def validate_samples(self, value):
        errors = []
        for i, row in enumerate(value):
            if not isinstance(row, dict):
                errors.append(f"Item {i + 1} must be an object.")
                continue
            comp_sum = 0.0
            for e in HV_ELEMENTS:
                if e in row and row[e] is not None:
                    try:
                        v = float(row[e])
                    except (TypeError, ValueError):
                        errors.append(f"Item {i + 1}: element {e} must be a valid number.")
                        continue
                    if v < 0 or v > 100:
                        errors.append(f"Item {i + 1}: element {e} must be between 0 and 100.")
                    comp_sum += max(v, 0.0)
            if comp_sum <= 0:
                errors.append(f"Item {i + 1}: the total of the 15 element compositions must be greater than 0.")
        if errors:
            raise serializers.ValidationError(errors)
        return value

class PredictionRecordSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = PredictionRecord
        fields = '__all__'
        read_only_fields = ['created_at']
