from rest_framework.routers import DefaultRouter
from apps.campus_nav.views import CampusLocationViewSet

router = DefaultRouter()
router.register(r'locations', CampusLocationViewSet, basename='location')

urlpatterns = router.urls