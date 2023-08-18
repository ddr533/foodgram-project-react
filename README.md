[![Main Foodgram workflow](https://github.com/ddr533/foodgram-project-react/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/ddr533/foodgram-project-react/actions/workflows/main.yaml)

[FoodGram](https://drogal-foodgram.ddns.net)

## FoodGram 
### Описание проекта  (Readme в разработке)
«Продуктовый помощник». С помощью сервиса пользователи могут публиковать рецепты, подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов, необходимых для приготовления
одного или нескольких выбранных блюд.

### Основные возможности
* Работа с рецептами (просмотр, публикация, добавление в избранное и т.п.).
* Административная панель для управления сайтом.
* Получение данных по API.

### Технологии 
  
 - Python  
 - Django
 - Django rest_framework
 - Docker
 - PostgreSQL
 - React

### Запуск проекта на сервере c ОС Linux
* Установить Докер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
sudo systemctl status docker
```
* Установить и настроить nginx на свободный порт (см. nginx.default.example):
```
sudo apt install nginx -y
sudo systemctl start nginx
sudo nano /etc/nginx/sites-enabled/default
sudo nginx -t
sudo service nginx reload
```
* Создать папку foodgram и скопировать в нее файл docker-compose.production.yml и папку data
* В папке foodgram создать и заполнить файл с переменными окружен .env (см. env.example)
* Запустить docker compose:
```
sudo docker compose -f docker-compose.production.yml up -d
```
* Выполнить миграции, собрать статические файлы бэкенда и скопировать их в /backend_static/static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
* Загрузить данные в БД:
```
docker compose exec -it backend python manage.py parse_json data/ingredients.json
```
* Создать адмнистратора для управления сайтом:
```
docker compose exec -it backend python manage.py createsuperuser
```

### Запуск проекта в контейнерах локально на Windows

* Установить Docker Desktop и WSL. Запустить Doker Desktop.
* Скачать проект:
  ```git clone git@github.com:ddr533/foodgram-project-react.git```
* В файле  .env указать данные для БД. 
* Перейти в папку с проектом и выполнить команду:
  ```
   docker-compose up -d
  ```
* Выполнить миграции: 
  ```
  docker compose exec backend python manage.py migrate
  ```
* Собрать и скопировать статику:
  ```
  docker compose exec backend python manage.py collectstatic
  ```
  ```
  docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
  ```
* Загрузить данные в БД:
  ```
  docker compose exec -it backend python manage.py parse_json ./data/ingredients.json
  ```
* Создать адмнистратора для управления сайтом:
  ```
  docker compose exec -it backend python manage.py createsuperuser
  ```
* Перейти в браузере по адресу 127.0.0.1:8000

### Примеры запросов API:
* Создание нового пользователя (POST):
  
  - api/users/
```
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}

``` 
* Получение токена для аутентификации (POST): 

  - api/token/login/
```
{
  "password": "string",
  "email": "string"
}

```
* Создать рецепт (POST)
  - api/recipes/
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
* Получить рецепты (GET)
  - api/recipes/
  - параметры:
```
page	- integer.  Номер страницы.
limit	- integer. Количество объектов на странице.
is_favorited - integer Enum: 0 1. Рецепты из избранного.
is_in_shopping_cart	- integer Enum: 0 1. Рецепты из корзины.
author - integer. Рецепты автора с указанным id.
tags	Array of strings. Пример: tags=lunch&tags=breakfast Рецепты с указанными тегами (по slug).
```
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
* Получить ингредиенты (GET):
  - api/ingredients/
  - паоаметры:
```
name - string. Поиск по частичному вхождению в начале названия ингредиента.
```
```
[
  {
    "id": 0,
    "name": "Капуста",
    "measurement_unit": "кг"
  }
]
```
* Получить теги (GET):
  - api/tags/
```
[
  {
    "id": 0,
    "name": "Завтрак",
    "color": "#E26C2D",
    "slug": "breakfast"
  }
]
```
* Получить ингредиент (GET):
```
api/ingredients/{id}/
```
* Получить тег (GET):
```
api/tags/{id}/
```
* Получить рецепт (GET), редактировать (PATCH) и удалить (DELETE) свой рецепт:
  - api/recipes/{id)
* Добавить (POST) или удалить (DELETE) рецепт из корзины:
  - api/recipes/{id}/shopping_cart/
* Скачать список покупок (GET):
  - api/recipes/download_shopping_cart/
* Добавить (POST) или удалить (DELETE) рецепт из избранного:
  - api/recipes/{id}/favorite/
* Подписаться (POST) и отменить (DELETE) подписку на автора:
  - api/users/{id}/subscribe/
* Посмотреть все подписки:
  - api/users/subscriptions/

### Автор:
Андрей Дрогаль (backend) & Yandex_Practicum (frontend)


