from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import check_password as django_check_password

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role='user'):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password, role='admin')
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # Django会自动处理密码哈希
    role = models.CharField(max_length=50)
    register_time = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        managed = False
        app_label = 'users'

    def __str__(self):
        return self.username

    def check_password(self, raw_password):
        """Validate passwords using Django's supported password hashers only."""
        return django_check_password(raw_password, self.password)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
        
    @property
    def is_staff(self):
        return self.role == 'admin'
        
    @property
    def is_admin(self):
        return self.role == 'admin'
        
    @property
    def is_active(self):
        return True  # 假设所有用户都是活跃的
        
    @property
    def is_superuser(self):
        return self.role == 'admin' 
