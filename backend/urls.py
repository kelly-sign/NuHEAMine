from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
import sys
import os
from django.conf import settings
from django.conf.urls.static import static

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from users.views import UserViewSet, RegisterView, LoginView, get_user_profile
from materials.views import MaterialViewSet, ProcessViewSet, RoomTempPropertyViewSet, HTPropertyViewSet, ImpTestViewSet, CreTestViewSet, FatTestViewSet, IrrConditionViewSet, MicrostructureEvolutionViewSet, EmbrittlementViewSet, HardeningViewSet, IrrCreepViewSet, DocumentViewSet
from predictions.views import (
    hv_predict,
    hv_predict_batch,
    prediction_under_development,
    prediction_history_list,
    prediction_history_detail,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'materials', MaterialViewSet, basename='materials')
router.register(r'processes', ProcessViewSet, basename='processes')
router.register(r'room-temp-properties', RoomTempPropertyViewSet, basename='room-temp-properties')
router.register(r'ht-properties', HTPropertyViewSet, basename='ht-properties')
router.register(r'imp-tests', ImpTestViewSet, basename='imp-tests')
router.register(r'cre-tests', CreTestViewSet, basename='cre-tests')
router.register(r'fat-tests', FatTestViewSet, basename='fat-tests')
router.register(r'irrconditions', IrrConditionViewSet, basename='irrconditions')
router.register(r'microstructures', MicrostructureEvolutionViewSet, basename='microstructures')
router.register(r'embrittlements', EmbrittlementViewSet, basename='embrittlements')
router.register(r'hardenings', HardeningViewSet, basename='hardenings')
router.register(r'irr-creeps', IrrCreepViewSet, basename='irr-creeps')
router.register(r'documents', DocumentViewSet, basename='documents')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Versioned prediction API. These paths intentionally have no trailing slash.
    path('api/v1/prediction/hardness', hv_predict, name='prediction-hardness'),
    path(
        'api/v1/prediction/yield_strength',
        prediction_under_development,
        name='prediction-yield-strength',
    ),
    path(
        'api/v1/prediction/tensile_strength',
        prediction_under_development,
        name='prediction-tensile-strength',
    ),
    path(
        'api/v1/prediction/phase',
        prediction_under_development,
        name='prediction-phase',
    ),
    path(
        'api/v1/prediction/irradiation_hardening',
        prediction_under_development,
        name='prediction-irradiation-hardening',
    ),
    path(
        'api/v1/prediction/irradiation_embrittlement',
        prediction_under_development,
        name='prediction-irradiation-embrittlement',
    ),
    # Legacy prediction endpoints remain available for the deployed hardness UI.
    path('api/predictions/hv/', hv_predict),
    path('api/predictions/hv/batch/', hv_predict_batch),
    path('api/predictions/history/', prediction_history_list),
    path('api/predictions/history/<int:pk>/', prediction_history_detail),
    path('api/', include(router.urls)),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/profile/', get_user_profile, name='profile'),
]

# 保持旧路径为兼容性
urlpatterns += [
    path('api/login/', LoginView.as_view(), name='login_legacy'),
    path('api/register/', RegisterView.as_view(), name='register_legacy'),
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh_legacy'),
]

# 添加媒体文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
