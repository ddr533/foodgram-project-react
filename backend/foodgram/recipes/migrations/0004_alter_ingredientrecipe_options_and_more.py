# Generated by Django 4.2.4 on 2023-08-10 03:33

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredientrecipe_recipe'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'ordering': ('recipe', 'id'), 'verbose_name': 'Ингридиенты рецепта', 'verbose_name_plural': 'Ингридиенты рецептов'},
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(5000)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингридиент'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(1000)], verbose_name='Время приготовления (минуты)'),
        ),
    ]
