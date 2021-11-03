from django.contrib.auth.models import User
from django.test import TestCase, Client

from api.models import UserProfile

c = Client()


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', first_name='Test',
                                             last_name='User', email='test@gmail.com')
        self.api_url = '/api/user/'

    def test_create_user(self):
        response = c.post(self.api_url, {'username': 'testuser2', 'password': '12345', 'first_name': 'Test',
                                         'last_name': 'User', 'email': 'test@gmail.com'})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(User.objects.get(username='testuser2').check_password('12345'), True)
        self.assertEqual(data['username'], 'testuser2')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['email'], 'test@gmail.com')

    def test_get_user_list(self):
        response = c.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data[0]['username'], 'testuser')
        self.assertEqual(len(data), User.objects.all().count())

    def test_get_user(self):
        response = c.get(self.api_url + '1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['email'], 'test@gmail.com')


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', first_name='Test',
                                             last_name='User')
        self.api_url = '/api/user-profile/'

    def test_create_user_profile(self):
        c.force_login(self.user)
        response = c.post(self.api_url, {'bio': '1234567890', 'location': 'Test Address'})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['bio'], '1234567890')
        self.assertEqual(data['location'], 'Test Address')

    def test_create_user_profile_ann(self):
        response = c.post(self.api_url, {'bio': '1234567890', 'location': 'Test Address'})
        self.assertEqual(response.status_code, 403)

    def test_get_user_profile(self):
        c.force_login(self.user)
        c.post(self.api_url, {'bio': '1234567890', 'location': 'Test Address'})
        response = c.get(self.api_url + '1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['bio'], '1234567890')
        self.assertEqual(data['location'], 'Test Address')

    def test_get_user_profile_ann(self):
        response = c.get(self.api_url + '1/')
        self.assertEqual(response.status_code, 403)

    def test_get_user_profile_list(self):
        c.force_login(self.user)
        response = c.get(self.api_url)
        self.assertEqual(response.status_code, 405)
