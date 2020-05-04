from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, GetRoutes

router = DefaultRouter()
router.register(r'routes', RouteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get_similar/', GetRoutes.as_view(), name='get_similar_routes')
]
