from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, SubscriptionViewSet


app_name = 'users'

router = DefaultRouter()
router.register(r'', CustomUserViewSet, basename='user')


urlpatterns = [
    path('subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}),
         name='user-subscriptions'),
    path('<int:author_id>/subscribe/',
         SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('', include(router.urls)),
]
