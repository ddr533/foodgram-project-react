from django.db import models


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
