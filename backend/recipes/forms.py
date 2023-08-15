from .models import Recipe, Tag
from .exceptions import *


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')
        widgets = {'color': forms.TextInput(attrs={'type': 'color'}),}


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        author = cleaned_data.get('author')
        recipe_name = self.cleaned_data['name']
        tags = self.cleaned_data['tag']
        recipe_id = self.instance.id

        duplicate = Recipe.objects.filter(
                author=author,
                name=recipe_name,
                tag__in=tags).exclude(id=recipe_id).first()
        if duplicate:
            raise DuplicateRecipeException(duplicate=duplicate)


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
