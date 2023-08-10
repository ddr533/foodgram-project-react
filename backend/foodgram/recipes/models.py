from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150,
        blank=False,
        db_index=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20,
        blank=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('id', 'name')

    def __str__(self):
        return self.name[:15]


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
        db_index=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        blank=False,
        verbose_name='Цвет(HEX)'
    )
    slug = models.SlugField(
        max_length=150,
        blank=False,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id', 'name')

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        db_index=True,
        verbose_name='Название'
    )
    text = models.TextField(
        max_length=5000,
        blank=False,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MaxValueValidator(1000)],
        blank=False,
        verbose_name='Время приготовления (минуты)'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        verbose_name='Фото'
    )
    tag = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Теги',
        blank=False,
    )
    ingredient = models.ManyToManyField(
        to=Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        blank=False,
        through='IngredientRecipe'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date', 'id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:25]


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        validators=[MaxValueValidator(5000)],
        blank=False,
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('recipe', 'id',)
        verbose_name = 'Ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'
