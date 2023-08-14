from django import forms

from .models import Recipe
from .exceptions import (DuplicateIngredientException,
                         MissingIngredientException,
                         MissingSelectionException,
                         MissingAmountException)



class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeIngredientInlineFormset(forms.models.BaseInlineFormSet):
    """
    Класс для работы со встроенной формой 'ингридиенты' в форме создания
    и редактирования рецепта в админ панели.
    """

    def clean(self):
        super().clean()
        ingredients = set()
        delete_counter = 0
        for form in self.forms:
            ingredient = form.cleaned_data.get('ingredient')
            amount = form.cleaned_data.get('amount')
            delete = form.cleaned_data.get('DELETE')

            if delete:
                delete_counter += 1
                continue

            if ingredient and amount:
                if ingredient not in ingredients:
                    ingredients.add(ingredient)
                    continue
                raise DuplicateIngredientException(ingredient)
            elif ingredient and not amount:
                raise MissingAmountException(ingredient)
            elif amount and not ingredient:
                raise MissingIngredientException

        if delete_counter == len(self.forms):
            raise MissingSelectionException()

        if not ingredients:
            raise MissingSelectionException()
