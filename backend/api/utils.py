from django.db.models import QuerySet
from recipes.models import IngredientRecipe


def get_ingredients_for_download(queryset: QuerySet[IngredientRecipe]) -> str:
    """
    Принимает на вход queryset с даннными ингридиентов рецептов.
    Формирует и возвращает строку с представлением
    полученных данных в виде списка объекта.
    """

    ingredient_list: list = ['Список покупок:', ]
    for ingredient in queryset:
        line = (f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' — {ingredient["amount"]}')
        ingredient_list.append(line)
    response_content = '\n'.join(ingredient_list)
    return response_content
