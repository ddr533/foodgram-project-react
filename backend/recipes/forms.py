from django import forms
from rest_framework.exceptions import ValidationError

from .exceptions import DuplicateIngredientException, \
    MissingIngredientException, MissingSelectionException, \
    MissingAmountException
from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeIngredientInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        ingredients = set()
        for form in self.forms:
            ingredient = form.cleaned_data.get('ingredient')
            amount = form.cleaned_data.get('amount')
            if ingredient and amount:
                if ingredient not in ingredients:
                    ingredients.add(ingredient)
                    continue
                raise DuplicateIngredientException(ingredient)
            elif ingredient and not amount:
                raise MissingAmountException(ingredient)
            elif amount and not ingredient:
                raise MissingIngredientException

        if not ingredients:
            raise MissingSelectionException()
