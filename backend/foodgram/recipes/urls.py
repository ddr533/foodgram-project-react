from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet


app_name = 'recipes'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    # path('ingredients/', SubscriptionViewSet.as_view({'get': 'list'}),
    #      name='ingredients'),
    path('', include(router.urls)),
]
