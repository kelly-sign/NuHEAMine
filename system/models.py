from django.db import models

class SystemLog(models.Model):
    LOG_LEVELS = (
        ('INFO', '信息'),
        ('WARNING', '警告'),
        ('ERROR', '错误'),
        ('DEBUG', '调试'),
    )
    
    LOG_TYPES = (
        ('USER', '用户操作'),
        ('SYSTEM', '系统操作'),
        ('SECURITY', '安全相关'),
        ('PERFORMANCE', '性能相关'),
    )
    
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField()
    user = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-created_at']

class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configs' 