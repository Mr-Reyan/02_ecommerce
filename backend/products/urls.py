from rest_framework.routers import DefaultRouter

from .views import ProductViewSet

router = DefaultRouter()

router.register(r"products", ProductViewSet, basename="prodcuts")


urlpatterns = []
urlpatterns += router.urls
