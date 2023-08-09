from rest_framework import mixins, viewsets, filters
from .serializers import IngredientsSerializer
from .models import Ingredient
from .filters import IngredientsSearch


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientsSearch,)
    pagination_class = None
