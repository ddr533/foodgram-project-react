from django.contrib import admin
from .models import Ingredient, Tag


class AdminIngredient(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('name',)


class AdminTag(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Ingredient, AdminIngredient)
admin.site.register(Tag, AdminTag)
