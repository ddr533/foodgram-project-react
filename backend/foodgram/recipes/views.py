import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from .serializers import (IngredientsSerializer,
                          TagSerializer,
                          RecipeSerializer)
from .models import Ingredient, Tag, Recipe
from .filters import IngredientsSearch, RecipeFilter
from .permissions import IsAuthorOrReadOnly


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsSearch,)
    pagination_class = None


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly,]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter]
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date', )
    ordering = ('pub_date',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
