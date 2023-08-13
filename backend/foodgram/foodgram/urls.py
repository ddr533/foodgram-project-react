from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls', namespace='recipes')),
    path('api/users/', include('users.urls', namespace='users')),
    path('api/auth/', include('djoser.urls.authtoken'), name='djoser_token'),
]

# Маршрут библиотеки для тестирования скорости запросов в БД.
# urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
