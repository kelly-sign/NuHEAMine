from django.db import models


class PredictionRecord(models.Model):
    prediction_type = models.CharField(max_length=50, default='hv')  # 仅保留 HV 单模型
    input_data = models.JSONField()
    output_data = models.JSONField()
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction_records'
        managed = False