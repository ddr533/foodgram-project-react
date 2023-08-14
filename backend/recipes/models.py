from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()

CHARS_MAX_LEN = 150
RECIPE_NAME_MAX_LEN = 200
RECIPE_TEXT_MAX_LEN = 5000
MEASUREMENT_UNIT_MAX_LEN = 20
HEX_COLOR_MAX_LEN = 7
MAX_COOKING_TIME = 1000
MAX_AMOUNT_INGREDIENT = 3000
STR_REPR_LEN = 20


class Ingredient(models.Model):
    """Ингредиенты для рецептов."""

    name = models.CharField(
        max_length=CHARS_MAX_LEN,
        blank=False,
        db_index=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LEN,
        blank=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('id', 'name')

    def __str__(self):
        return self.name[:STR_REPR_LEN]


class Tag(models.Model):
    """Теги для рецептов."""

    name = models.CharField(
        max_length=CHARS_MAX_LEN,
        blank=False,
        unique=True,
        db_index=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=HEX_COLOR_MAX_LEN,
        blank=False,
        verbose_name='Цвет(HEX)'
    )
    slug = models.SlugField(
        max_length=CHARS_MAX_LEN,
        blank=False,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id', 'name')

    def __str__(self):
        return self.name[:STR_REPR_LEN]


class Recipe(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LEN,
        blank=False,
        verbose_name='Название'
    )
    text = models.TextField(
        max_length=RECIPE_TEXT_MAX_LEN,
        blank=False,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_COOKING_TIME)],
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
        db_index=True,
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
        return self.name[:STR_REPR_LEN]


class IngredientRecipe(models.Model):
    """Модель для связи ингредиентов и рецептов."""

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
        validators=[MaxValueValidator(MAX_AMOUNT_INGREDIENT)],
        blank=False,
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('recipe', 'id',)
        verbose_name = 'Ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'


class Favorite(models.Model):
    """Модель для добавления в БД избранных рецептов пользователей."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранные рецепты',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=('user', 'recipe'),
                             name='unique_user_and_favorite_recipe')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.recipe}'


class BuyList(models.Model):
    """Модель для добавления в БД рецептов для покупки пользователями."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='buylist_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='buylist',
        verbose_name='Список покупок',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            UniqueConstraint(fields=('user', 'recipe'),
                             name='unique_user_and_buylist_recipe')
        ]

    def __str__(self):
        return f'{self.user} покупает {self.recipe}'
