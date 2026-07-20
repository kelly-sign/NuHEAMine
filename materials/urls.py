from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, ProcessViewSet, RoomTempPropertyViewSet, HTPropertyViewSet, ImpTestViewSet, CreTestViewSet, FatTestViewSet, IrrConditionViewSet, MicrostructureEvolutionViewSet, EmbrittlementViewSet, HardeningViewSet, IrrCreepViewSet

router = DefaultRouter()
router.register(r'materials', MaterialViewSet)
router.register(r'processes', ProcessViewSet)
router.register(r'room-temp-properties', RoomTempPropertyViewSet, basename='room-temp-properties')
router.register(r'ht-properties', HTPropertyViewSet, basename='ht-properties')
router.register(r'imp-tests', ImpTestViewSet, basename='imp-tests')
router.register(r'cre-tests', CreTestViewSet, basename='cre-tests')
router.register(r'fat-tests', FatTestViewSet, basename='fat-tests')
router.register(r'irr-conditions', IrrConditionViewSet, basename='irr-conditions')
router.register(r'microstructures', MicrostructureEvolutionViewSet, basename='microstructures')
router.register(r'embrittlements', EmbrittlementViewSet, basename='embrittlements')
router.register(r'hardenings', HardeningViewSet, basename='hardenings')
router.register(r'irr-creeps', IrrCreepViewSet, basename='irr-creeps')

urlpatterns = [
    path('', include(router.urls)),
] 
