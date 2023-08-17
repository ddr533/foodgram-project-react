import re

from rest_framework.exceptions import ValidationError


def validate_hex_color(value):
    """Проверяет, что строка соответствует кодировке цвета HEX."""

    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not re.match(pattern, value):
        raise ValidationError('Некорректный формат HEX-цвета')
