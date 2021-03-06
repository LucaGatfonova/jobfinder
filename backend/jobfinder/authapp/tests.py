from django.test import TestCase, Client
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APIClient, APITestCase

from .models import CustomUser
from .views import CustomUserModelViewSet


class TestCustomUserViewSet(TestCase):
    url = '/api/v1/user/'

    def setUp(self) -> None:
        self.admin = CustomUser.objects.create_superuser('admin', 'admin@admin.com', 'admin123456')
        self.user = CustomUser.objects.create(username='test_user', email='test@mail.ru', password='qazwsx', role=2)
        self.user.save()

    def test_get_list(self):
        factory = APIRequestFactory()
        request = factory.get(self.url)
        force_authenticate(request, self.admin)
        view = CustomUserModelViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_admin(self):
        factory = APIRequestFactory()
        request = factory.post(self.url, {'username': 'test_user_x', 'password': 'qazwsx123',
                                          'email': 'mail222@mail.ru', 'role': 2}, format='json')
        force_authenticate(request, self.admin)
        view = CustomUserModelViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_detail(self):
        client = APIClient()
        response = client.get(f'{self.url}{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authapp_registration_exist(self):
        response = self.client.post('/api/v1/user/', {
            "email": "test@mail.ru",
            "username": "test_user",
            "password": "qazwsx",
            "role": "2"
        })
        self.assertEqual(response.status_code, 400)

    def test_bearer_token(self):
        user = CustomUser.objects.get(id=1)

        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    def test_authapp_create_jwt(self):
        response = self.client.post('/api/v1/token/', data={
            "username": "test_user",
            "password": "admin123456789"
        })
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/token/', data={
            "username": "admin",
            "password": "admin123456"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'refresh', status_code=200)
        self.assertContains(response, 'access', status_code=200)

    def tearDown(self) -> None:
        pass

