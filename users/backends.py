from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 尝试查找用户
            user = User.objects.get(username=username)
            
            # 使用Django的check_password方法验证密码
            if user.check_password(password):
                return user
            else:
                logger.warning("Authentication rejected: invalid credentials")
                return None
        except User.DoesNotExist:
            logger.warning("Authentication rejected: invalid credentials")
            return None
        except Exception:
            logger.exception("Unexpected authentication error")
            return None 
