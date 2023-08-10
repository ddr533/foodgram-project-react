from django.contrib import admin
from .models import Ingredient, Tag, Recipe, IngredientRecipe
from .forms import RecipeForm


class AdminIngredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('measurement_unit',)
    list_filter = ('name',)


class AdminTag(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class AdminIngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class AdminRecipe(admin.ModelAdmin):
    form = RecipeForm
    inlines = [AdminIngredientRecipeInline]
    list_display = ('id', 'name', 'author')
    list_editable = ('name', 'author')
    list_filter = ('name', 'author', 'tag')


class AdminIngredientRecipe(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_editable = ('ingredient', 'amount')


admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Tag, AdminTag)
admin.site.register(Recipe, AdminRecipe)
admin.site.register(IngredientRecipe, AdminIngredientRecipe)
