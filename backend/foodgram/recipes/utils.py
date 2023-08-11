def get_ingredients_for_download(queryset):
    """
    Принимает на вход queryset с нужными данными из БД.
    Формирует и возвращает строку с нужным представлением полученных данных.
    """

    ingredient_list = ['Список покупок:', ]
    for ingredient in queryset:
        line = (f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' — {ingredient["amount"]}')
        ingredient_list.append(line)
    response_content = '\n'.join(ingredient_list)
    return response_content
