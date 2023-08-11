from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet,
                    TagViewSet,
                    RecipeViewSet,
                    FavoriteViewSet, BuyListViewSet, DownloadShoppingCart)

app_name = 'recipes'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         BuyListViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart'),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view(),
         name='download_shopping_cart'),
    path('', include(router.urls)),
]
