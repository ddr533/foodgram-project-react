from django.contrib import admin
from .models import (Ingredient, Tag, Recipe, IngredientRecipe, Favorite,
                     BuyList)
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
    readonly_fields = ('id', 'total_favorite_count',)

    def total_favorite_count(self, obj):
        return obj.favorites.count()

    total_favorite_count.short_description = 'Количество добавлений в избранное'


class AdminIngredientRecipe(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_editable = ('ingredient', 'amount')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


class BuyListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Tag, AdminTag)
admin.site.register(Recipe, AdminRecipe)
admin.site.register(IngredientRecipe, AdminIngredientRecipe)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(BuyList, BuyListAdmin)
