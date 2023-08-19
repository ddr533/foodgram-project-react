from django import forms


class DuplicateRecipeException(forms.ValidationError):
    def __init__(self, duplicate):
        tag_str = ', '.join(tag.name for tag in duplicate.tag.all())
        super().__init__(
            'У данного автора есть похожий рецепт. '
            f'Название: {duplicate.name}. Теги: {tag_str}')


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


class DuplicateTagException(forms.ValidationError):
    def __init__(self):
        super().__init__('Этот рецепт уже есть в корзине.')


class RequiredField(forms.ValidationError):
    def __init__(self, field_name):
        super().__init__(f'Поле {field_name} обязательно для заполнения.')
