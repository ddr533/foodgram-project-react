import base64
import json
import shutil
import tempfile
from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from PIL import Image
from recipes.models import (BuyList, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def get_image_base64():
    """Создает картинку в base64."""
    image = Image.new('RGB', (10, 10), color='red')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_data = buffer.getvalue()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    return 'data:image/png;base64,' + base64_image


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipeTests(TestCase):
    """
    Тесты для маршрутов, связанных с рецептами.

    Предполагается, что автор рецепта может добавлять свой же рецепт в корзину
    и избранное. В противном случае необходимо создать еще одного пользователя.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='author',
            email='user1@example.com',
            password='password1')
        cls.ingredient1 = Ingredient.objects.create(
            name='Ингредиент 1',
            measurement_unit='г')
        cls.ingredient2 = Ingredient.objects.create(
            name='Ингредиент 2',
            measurement_unit='мл')
        cls.tag1 = Tag.objects.create(name='Т1', color='#FF0000', slug='tag-1')
        cls.tag2 = Tag.objects.create(name='Т2', color='#00FF00', slug='tag-2')
        cls.recipe = Recipe.objects.create(
            author=cls.author,
            name='Название рецепта',
            text='Описание рецепта',
            cooking_time=60,
            image='recipes/images/recipe_test.jpg',
        )
        cls.recipe.tag.add(cls.tag1, cls.tag2)
        IngredientRecipe.objects.create(
            ingredient=cls.ingredient1,
            recipe=cls.recipe,
            amount=100
        )
        IngredientRecipe.objects.create(
            ingredient=cls.ingredient2,
            recipe=cls.recipe,
            amount=200
        )
        cls.url_list = reverse('api:recipes-list')
        cls.url_detail = reverse('api:recipes-detail',
                                 kwargs={'pk': cls.recipe.id})
        cls.image = get_image_base64()
        cls.buy_recipe_url = reverse('api:shopping_cart',
                                     kwargs={'recipe_id': cls.recipe.id})
        cls.favorite_recipe_url = reverse('api:favorite',
                                          kwargs={'recipe_id': cls.recipe.id})

    def setUp(self):
        self.anon = APIClient()
        self.client = APIClient()
        response = self.client.post('/api/auth/token/login/', {
            'email': 'user1@example.com',
            'password': 'password1'
        })
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='token ' + self.token)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_anonymous_user_can_get_recipe_list(self):
        """Анонимный пользователь может получить рецепты."""
        response = self.anon.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.anon.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recipe_contains_all_fields(self):
        """Рецепт содержит все необходимые поля указанные в сериализаторе."""
        expected_fields = {'name', 'author', 'id', 'tags', 'ingredients',
                           'text', 'cooking_time', 'image',
                           'is_in_shopping_cart', 'is_favorited'}
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected_fields, set(response.data.keys()))

    def test_authenticated_user_can_create_recipe(self):
        """Авторизованный пользователь может создать рецепт."""
        recipes_count = Recipe.objects.count()
        data = {
            'name': 'New Recipe',
            'text': 'Описание нового рецепта',
            'cooking_time': 45,
            'image': self.image,
            'tags': [self.tag1.id, self.tag2.id],
            'ingredients': [{'id': self.ingredient1.id, 'amount': 100}]
        }
        json_data = json.dumps(data)
        response = self.client.post(self.url_list, json_data,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), recipes_count + 1)
        self.assertEqual(Recipe.objects.latest('id').name, 'New Recipe')
        self.assertEqual(Recipe.objects.latest('id').author, self.author)

    def test_authenticated_user_can_delete_own_recipe(self):
        """Авторизованный пользователь может удалить свой рецепт."""
        recipes_count = Recipe.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), recipes_count - 1)

    def test_authenticated_user_can_edit_recipe(self):
        data = self.client.get(self.url_detail).data
        data['name'] = 'Patchme'
        data['tags'] = [tag['id'] for tag in data['tags']]
        data['image'] = self.image
        response = self.client.patch(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.get(id=self.recipe.id).name, 'Patchme')

    def test_authenticated_user_can_add_recipe_to_favorite(self):
        """Авторизованный пользователь может добавить рецепт в избранное."""
        response = self.client.post(self.favorite_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.author.favorite_set.count(), 1)
        self.assertEqual(self.author.favorite_set.first().recipe,
                         self.recipe)

    def test_authenticated_user_can_remove_recipe_from_favorite(self):
        """Авторизованный пользователь может удалить рецепт из избранного."""
        Favorite.objects.create(user=self.author, recipe=self.recipe)
        response = self.client.delete(self.favorite_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.author.favorite_set.count(), 0)

    def test_authenticated_user_can_add_recipe_to_shopping_cart(self):
        """Авторизованный пользователь может добавить рецепт в корзину."""
        response = self.client.post(self.buy_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.author.buylist_set.count(), 1)
        self.assertEqual(self.author.buylist_set.first().recipe,
                         self.recipe)

    def test_authenticated_user_can_remove_recipe_from_shopping_cart(self):
        """Авторизованный пользователь может удалить рецепт из корзины."""
        BuyList.objects.create(user=self.author, recipe=self.recipe)
        response = self.client.delete(self.buy_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.author.buylist_set.count(), 0)

    def test_anonymous_user_cannot_add_recipe_to_favorite(self):
        """Аноним не может добавить рецепт в избранное."""
        response = self.anon.post(self.favorite_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_add_recipe_to_shopping_cart(self):
        """Аноним не может добавить рецепт в корзину."""
        response = self.anon.post(self.buy_recipe_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserRegistrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='password1',
        )
        cls.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='password2',
        )

    def setUp(self):
        self.anon = APIClient()
        self.client = APIClient()
        response = self.client.post('/api/auth/token/login/', {
            'email': 'user1@example.com',
            'password': 'password1'
        })
        self.token = response.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='token ' + self.token)

    def test_users_list_and_detail_pages(self):
        """Все пользователи могут просматривать список юзеров и их профили."""
        url_list = reverse('api:user-list')
        url_detail = reverse('api:user-detail', kwargs={'id': self.user1.id})
        response = self.anon.get(url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.anon.get(url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_can_register(self):
        """Пользователь может зарегистрироваться с корректными данными."""
        url = reverse('api:user-list')
        data = {
            'email': 'test@example.com',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'username': 'testuser',
            'password': 'testpassword',
        }
        user_counts = User.objects.count()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)
        self.assertEqual(User.objects.count(), user_counts + 1)

    def test_anonymous_user_cant_register(self):
        """Пользователь не может зарегистроваться с некорректными данными."""
        url = reverse('api:user-list')
        data = {'username': 'notuser', 'password': 'testpassword'}
        self.client.post(url, data)
        self.assertFalse(User.objects.filter(username='notuser').exists())

    def user_can_change_password(self):
        """Пользователь может поменять пароль."""
        data = {'current_password': 'password1',
                'new_password': 'testpasswordnew', }
        url = 'api/auth/token/login'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {'current_password': 'testpasswordnew',
                'new_password': 'password1', }
        self.client.post(url, data)

    def test_user_can_subscribe(self):
        """Авторизованный пользователь может оформить подписку.
        В response ответа есть все ожидаемые поля."""
        expected_fields = {'email', 'username', 'id', 'first_name',
                           'last_name', 'is_subscribed', 'recipes',
                           'recipes_count'}
        url = reverse('api:subscribe', kwargs={'author_id': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user2.subscribed.count(), 1)
        self.assertEqual(expected_fields, set(response.data.keys()))

    def test_anon_cant_subscribe(self):
        """Анонимный пользователь не может оформлять подписки."""
        url = reverse('api:subscribe', kwargs={'author_id': self.user2.id})
        response = self.anon.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.user2.subscribed.count(), 0)

    def test_user_can_unsubscribe(self):
        """Пользователь может отменить подписку."""
        url = reverse('api:subscribe', kwargs={'author_id': self.user2.id})
        response = self.client.post(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user2.subscribed.count(), 0)

    def test_user_cannot_subscribe_to_same_author_twice(self):
        """Пользователь не может подписаться дважды на одного автора."""
        url = reverse('api:subscribe', kwargs={'author_id': self.user2.id})
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user2.subscribed.count(), 1)

    def test_user_me_page_accessible(self):
        """Доступна страница users/me/ для авторизованного пользователя."""
        url = reverse('api:user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)

    def test_anonymous_user_cannot_access_me_page(self):
        """Cтраница users/me/ не доступна анонимному пользователю."""
        url = reverse('api:user-me')
        response = self.anon.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail_endpoint(self):
        """Пользователь не может редактировать страницу профиля."""
        url = reverse('api:user-detail', kwargs={'id': self.user1.id})
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)

    def test_user_me_endpoint(self):
        """Пользователь не может редактировать свою страницу me."""
        url = reverse('api:user-me')
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(url, data={})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
