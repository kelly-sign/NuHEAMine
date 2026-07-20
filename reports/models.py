from django.db import models

class Report(models.Model):
    REPORT_TYPES = (
        ('performance', '性能分析报告'),
        ('prediction', '预测结果报告'),
        ('statistics', '统计分析报告'),
    )
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    content = models.JSONField()  # 存储报告内容
    file = models.FileField(upload_to='reports/', null=True, blank=True)  # 存储生成的文件
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']

class ReportTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    template_file = models.FileField(upload_to='templates/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'report_templates' 