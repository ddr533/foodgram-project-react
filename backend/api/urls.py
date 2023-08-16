from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from .views import (BuyListViewSet, CustomUserViewSet, DownloadShoppingCart,
                    FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    SubscriptionViewSet, TagViewSet)

app_name = 'recipes'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', CustomUserViewSet, basename='user')


urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         BuyListViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopping_cart'),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view(),
         name='download_shopping_cart'),
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}),
         name='user-subscriptions'),
    path('users/<int:author_id>/subscribe/',
         SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'}),
         name='set_password'),
    path('auth/', include('djoser.urls.authtoken'), name='djoser_token'),
    path('', include(router.urls)),
]
