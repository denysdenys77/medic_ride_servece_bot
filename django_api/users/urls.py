from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from users import views

router = DefaultRouter()
router.register(r'users', views.ServiceUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('delete-user/<int:telegram_id>/', views.service_user_delete, name='delete_user')
]
