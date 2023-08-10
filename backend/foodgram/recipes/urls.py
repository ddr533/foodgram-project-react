from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet,
                    TagViewSet,
                    RecipeViewSet,
                    FavoriteViewSet)

app_name = 'recipes'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view(
             {'post': 'create', 'delete': 'destroy'}), name='favorite'),
    path('', include(router.urls)),
]
