import random
import string


def generate_secret_key():
    """Генерирует дефолтный секретный ключ джанго."""

    chars = string.ascii_letters + string.digits + string.punctuation
    key = ''.join(random.choice(chars) for _ in range(50))
    return 'django-insecure-' + key


if __name__ == '__main__':
    print(generate_secret_key())
