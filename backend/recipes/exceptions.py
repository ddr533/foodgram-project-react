from django import forms


class DuplicateRecipeException(forms.ValidationError):
    def __init__(self):
        super().__init__('Рецепт с таким именем уже есть у автора.')


class DuplicateIngredientException(forms.ValidationError):
    def __init__(self, ingredient_name):
        super().__init__(f'Этот ингредиент уже есть'
                         f' в рецепте: {ingredient_name}.')


class MissingAmountException(forms.ValidationError):
    def __init__(self, ingredient):
        super().__init__(f'Укажите количество ингредиента {ingredient}.')


class MissingIngredientException(forms.ValidationError):
    def __init__(self):
        super().__init__('Укажите ингредиент и его количество.')


class MissingSelectionException(forms.ValidationError):
    def __init__(self):
        super().__init__('Выберите хотя бы 1 ингредиент и его количество.')
