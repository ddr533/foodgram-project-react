## FoodGram 
#### Описание проекта  (Readme в разработке)


#### Запуск проекта на Windows в режиме разработки 

* Установить Docker Desktop и WSL. Запустить Doker Desktop
* Скачать проект
  ```git clone git@github.com:ddr533/foodgram-project-react.git```
* В файле  .env при необходимости указать свои данные для БД. (При развертывании проекта локально без контейнеризации установить для БД HOST=localhost) 
* Перейти в папку с проектом и выполнить команду docker-compose up
* В новом cmd окне выполнить:
  ```
  docker compose exec backend python manage.py migrate
  ```
  ```
  docker compose exec backend python manage.py collectstatic
  ```
  ```
  docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
  ```
  ```
  docker compose exec backend python manage.py parse_json ./data/ingredients.json
  ```
  ```
  docker compose exec backend python manage.py createsuperuser
  ```
* Перейти в браузере по адресу 127.0.0.1:8000 
  
