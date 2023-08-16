from django.contrib import admin

from .forms import RecipeForm, RecipeIngredientInlineFormset, TagForm
from .models import (BuyList, Favorite, Ingredient, IngredientRecipe, Recipe,
                     Tag)


class AdminIngredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('measurement_unit',)
    list_filter = ('name',)


class AdminTag(admin.ModelAdmin):
    form = TagForm
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class AdminIngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    formset = RecipeIngredientInlineFormset


class AdminRecipe(admin.ModelAdmin):
    form = RecipeForm
    inlines = [AdminIngredientRecipeInline]
    list_display = ('id', 'name', 'author')
    list_filter = ('name', 'author', 'tag')
    readonly_fields = ('id', 'total_favorite_count',)

    def total_favorite_count(self, obj):
        return obj.favorite_set.count()

    total_favorite_count.short_description = ('Количество добавлений'
                                              ' в избранное')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


class BuyListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Tag, AdminTag)
admin.site.register(Recipe, AdminRecipe)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(BuyList, BuyListAdmin)
