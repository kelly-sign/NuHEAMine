from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer
from .models import User
import logging

logger = logging.getLogger(__name__)


class IsPlatformAdministrator(BasePermission):
    """Allow user-management operations to platform administrators only."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'admin'
        )

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            except Exception:
                logger.exception("Registration failed")
                return Response({
                    'message': 'Registration failed. Please check the submitted information.'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # 尝试直接查询用户
            try:
                user_obj = User.objects.get(username=username)
                
                # 直接验证密码
                if user_obj.check_password(password):
                    refresh = RefreshToken.for_user(user_obj)
                    return Response({
                        'user': UserSerializer(user_obj).data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    logger.warning("Login rejected: invalid credentials")
            except User.DoesNotExist:
                logger.warning("Login rejected: invalid credentials")
            except Exception:
                logger.exception("Unexpected login error")
            
            # 如果直接验证失败，尝试使用Django的authenticate
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
                
            logger.warning("Login rejected: invalid credentials")
            return Response({
                'message': 'Invalid username or password.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsPlatformAdministrator]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        serializer = UserSerializer(request.user)
        return Response({
            'user': serializer.data
        })
    except Exception:
        logger.exception("Unable to load user profile")
        return Response({
            'message': 'Unable to load the user profile.'
        }, status=status.HTTP_400_BAD_REQUEST) 
