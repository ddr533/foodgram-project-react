from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, Q, F, UniqueConstraint


EMAIL_MAX_LEN = 254
CHARS_MAX_LEN = 150
VALIDATE_USERNAME_MSG = ('Username может содержать только буквы,'
                         ' цифры или следующие символы: @/./+/-/_')


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_MAX_LEN,
        blank=False,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=CHARS_MAX_LEN,
        unique=True,
        blank=False,
        verbose_name='Никнейм',
        validators=[
            RegexValidator(regex=r'^[\w.@+-]+$',message=VALIDATE_USERNAME_MSG)
        ],
    )
    first_name = models.CharField(
        max_length=CHARS_MAX_LEN,
        verbose_name='Имя',
        blank=False,
    )
    last_name = models.CharField(
        max_length=CHARS_MAX_LEN,
        verbose_name='Фамилия',
        blank=False,
    )
    password = models.CharField(
        max_length=CHARS_MAX_LEN,
        verbose_name='Пароль')

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', 'username')

    def __str__(self):
        return self.get_full_name()


class Subscription(models.Model):
    """Модель для добавления в БД подписок пользователей на авторов рецептов."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Подписан на',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            CheckConstraint(check=~Q(user=F('author')),
                            name='user!=author'),
            UniqueConstraint(fields=('user', 'author'),
                             name='unique_name_and_author')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
