from rest_framework.routers import DefaultRouter
from connectivity.views import DatabaseConnectionViewSet

router = DefaultRouter()
router.register(r'connections', DatabaseConnectionViewSet, basename='connection')

urlpatterns = router.urls