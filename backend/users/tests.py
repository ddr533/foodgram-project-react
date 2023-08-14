from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


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

    def test_anonymous_user_can_register(self):
        """Пользователь может зарегистрироваться с корректными данными."""
        url = reverse('users:user-list')
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
        url = reverse('users:user-list')
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
        url = reverse('users:subscribe', kwargs={'author_id': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user2.subscribed.count(), 1)
        self.assertEqual(expected_fields, set(response.data.keys()))

    def test_anon_cant_subscribe(self):
        """Анонимный пользователь не может оформлять подписки."""
        url = reverse('users:subscribe', kwargs={'author_id': self.user2.id})
        response = self.anon.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.user2.subscribed.count(), 0)

    def test_user_can_unsubscribe(self):
        """Пользователь может отменить подписку."""
        url = reverse('users:subscribe', kwargs={'author_id': self.user2.id})
        response = self.client.post(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user2.subscribed.count(), 0)

    def test_user_cannot_subscribe_to_same_author_twice(self):
        """Пользователь не может подписаться дважды на одного автора."""
        url = reverse('users:subscribe', kwargs={'author_id': self.user2.id})
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user2.subscribed.count(), 1)

    def test_user_me_page_accessible(self):
        """Доступна страница users/me/ для авторизованного пользователя."""
        url = reverse('users:user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user1.username)

    def test_anonymous_user_cannot_access_me_page(self):
        """Cтраница users/me/ не доступна анонимному пользователю."""
        url = reverse('users:user-me')
        response = self.anon.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
