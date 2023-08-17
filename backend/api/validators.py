from typing import List, Type, Union

from django.db import models
from rest_framework import serializers


def validate_unique_for_list(
        name: str, data: List[Union[str, int, Type[models.Model]]]) -> None:
    """Проверяет, что в переданном списке уникальные id или объекты модели."""

    temp = set()
    for elem in data:
        if elem in temp:
            raise serializers.ValidationError(
                f'Поле {name} содержит повторяющийся элемент {elem}.')
        temp.add(elem)


def validate_number(name: str, num: int, max: int, min: int) -> None:
    if not isinstance(num, int) or not min <= num <= max:
        raise serializers.ValidationError(
            f'Поле {name} содержит не числовое или слишком большое '
            f'значение {num}.')
