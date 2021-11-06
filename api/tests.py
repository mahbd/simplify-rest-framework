from django.contrib.auth.models import User
from django.test import TestCase, Client

from api.models import Problem, Contest, TestCase as TestCaseModel

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


class ProblemTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', first_name='Test',
                                             last_name='User')
        self.api_url = '/api/problem/'
        c.force_login(self.user)
        c.post(self.api_url, {'title': 'Test Problem first', 'description': 'Test Description second',
                              'input_terms': 'hello world bad',
                              'output_terms': 'nice world bad'})
        c.logout()

    def test_create_problem(self):
        response = c.post(self.api_url, {'title': 'Test Problem', 'description': 'Test Description',
                                         'input_terms': 'hello world',
                                         'output_terms': 'nice world'})
        self.assertEqual(response.status_code, 201, f'{response.content}')
        data = response.json()
        self.assertEqual(data['title'], 'Test Problem')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['input_terms'], 'hello world')
        self.assertEqual(data['output_terms'], 'nice world')

    def test_problem_low_difficulty(self):
        c.force_login(self.user)
        response = c.post(self.api_url, {'title': 'Test Problem', 'description': 'Test Description',
                                         'input_terms': 'hello world',
                                         'output_terms': 'nice world', 'difficulty': 100})
        self.assertEqual(response.status_code, 400)

    def test_get_problem_list(self):
        response = c.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

    def test_get_problem(self):
        response = c.get(self.api_url + '1/')
        self.assertEqual(response.status_code, 200)

    def test_update_problem(self):
        c.force_login(self.user)
        response = c.put(self.api_url + '1/', data={'title': 'Test Problem', 'description': 'Test Description',
                                                    'input_terms': 'hello world',
                                                    'output_terms': 'nice world'}, content_type='application/json')
        self.assertEqual(response.status_code, 200, f'{response.content}')
        data = response.json()
        self.assertEqual(data['title'], 'Test Problem')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['input_terms'], 'hello world')
        self.assertEqual(data['output_terms'], 'nice world')

    def test_delete_problem(self):
        c.force_login(self.user)
        response = c.delete(self.api_url + '1/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Problem.objects.all().count(), 0)

    def test_update_problem_anonymous(self):
        response = c.put(self.api_url + '1/', data={'title': 'Test Problem', 'description': 'Test Description',
                                                    'input_terms': 'hello world',
                                                    'output_terms': 'nice world'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_delete_problem_anonymous(self):
        response = c.delete(self.api_url + '1/')
        self.assertEqual(response.status_code, 403)


class ContestTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', first_name='Test',
                                             last_name='User')
        self.api_url = '/api/contest/'
        c.force_login(self.user)
        c.post(self.api_url, {'title': 'Test Contest first', 'description': 'Test Description second',
                              'start_date': '2020-01-01', 'end_date': '2020-01-01'})
        c.logout()

    def test_create_contest(self):
        c.force_login(self.user)
        response = c.post(self.api_url, {'title': 'Test Contest', 'description': 'Test Description',
                                         'start_date': '2020-01-01', 'end_date': '2020-01-01'})
        self.assertEqual(response.status_code, 201, f'{response.content}')

    def test_create_contest_anonymous(self):
        response = c.post(self.api_url, {'title': 'Test Contest', 'description': 'Test Description',
                                         'start_date': '2020-01-01', 'end_date': '2020-01-01'})
        self.assertEqual(response.status_code, 403)

    def test_get_contest_list(self):
        response = c.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), Contest.objects.all().count())

    def test_get_contest_list_anon(self):
        response = c.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), Contest.objects.all().count())

    def test_get_contest(self):
        response = c.get(self.api_url + '1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Test Contest first')
        self.assertEqual(data['description'], 'Test Description second')

    def test_get_contest_anon(self):
        response = c.get(self.api_url + '1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Test Contest first')
        self.assertEqual(data['description'], 'Test Description second')

    def test_update_contest(self):
        c.force_login(self.user)
        response = c.put(self.api_url + '1/', data={'title': 'Test Contest', 'description': 'Test Description'},
                         content_type='application/json')
        self.assertEqual(response.status_code, 200, f'{response.content}')
        data = response.json()
        self.assertEqual(data['title'], 'Test Contest')
        self.assertEqual(data['description'], 'Test Description')

    def test_update_contest_anon(self):
        response = c.put(self.api_url + '1/', data={'title': 'Test Contest', 'description': 'Test Description'})
        self.assertEqual(response.status_code, 403)

    def test_delete_contest(self):
        c.force_login(self.user)
        response = c.delete(self.api_url + '1/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Contest.objects.all().count(), 0)

    def test_delete_contest_anon(self):
        response = c.delete(self.api_url + '1/')
        self.assertEqual(response.status_code, 403)

    def test_update_contest_non_permitted_user(self):
        user = User.objects.create_user(username='testuser2', password='12345', first_name='Test')
        c.force_login(user)
        response = c.put(self.api_url + '1/', data={'title': 'Test Contest', 'description': 'Test Description'})
        self.assertEqual(response.status_code, 403)

    def test_update_contest_writers(self):
        user = User.objects.create_user(username='testuser2', password='12345', first_name='Test')
        c.force_login(user)
        contest = Contest.objects.get(id=1)
        contest.writers.add(user)
        contest.save()
        response = c.put(self.api_url + '1/', data={'title': 'Test Contest', 'description': 'Test Description'},
                         content_type='application/json')
        self.assertEqual(response.status_code, 200)
        contest.refresh_from_db()
        self.assertEqual(Contest.objects.get(id=1).title, 'Test Contest')
        self.assertEqual(Contest.objects.get(id=1).description, 'Test Description')


class TestCaseTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='12345', first_name='Test')
        self.problem = Problem.objects.create(title='Test Problem', description='Test Description', user=self.user)
        self.test_case = TestCaseModel.objects.create(inputs='fsdaf', output='fdsjfkl', user=self.user,
                                                      problem=self.problem)
        self.api = '/api/test-case/'

    def test_create_test_case(self):
        c.force_login(self.user)
        response = c.post(self.api, data={'inputs': 'fsdaf', 'output': 'fdsjfkl', 'problem': self.problem.id},
                          content_type='application/json')
        self.assertEqual(response.status_code, 201, f'{response.content}')
        data = response.json()
        self.assertEqual(data['inputs'], 'fsdaf')
        self.assertEqual(data['output'], 'fdsjfkl')
        self.assertEqual(TestCaseModel.objects.all().count(), 2)

    def test_create_test_case_anon(self):
        response = c.post(self.api, data={'inputs': 'fsdaf', 'output': 'fdsjfkl', 'problem': self.problem.id},
                          content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_create_test_case_non_problem_writer(self):
        user = User.objects.create_user(username='testuser2', password='12345', first_name='Test')
        c.force_login(user)
        response = c.post(self.api, data={'inputs': 'fsdaf', 'output': 'fdsjfkl', 'problem': self.problem.id},
                          content_type='application/json')
        # ToDo: Fix this. This user should not be permitted to create test cases for this problem
        self.assertEqual(response.status_code, 201)

    def test_update_test_case(self):
        c.force_login(self.user)
        response = c.put(self.api + '1/', data={'inputs': 'fsdaf', 'output': 'fdsjfkl', 'problem': self.problem.id},
                         content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_partial_update_test_case(self):
        c.force_login(self.user)
        response = c.patch(self.api + '1/', data={'inputs': 'fsdaf', 'output': 'fdsjfkl', 'problem': self.problem.id},
                           content_type='application/json')
        self.assertEqual(response.status_code, 405)

    def test_delete_test_case(self):
        c.force_login(self.user)
        response = c.delete(self.api + '1/')
        self.assertEqual(response.status_code, 204)

    def test_delete_test_case_anon(self):
        response = c.delete(self.api + '1/')
        self.assertEqual(response.status_code, 403)

    def test_get_test_case_list(self):
        c.force_login(self.user)
        response = c.get(self.api)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), TestCaseModel.objects.all().count())

    def test_get_test_case_list_anon(self):
        response = c.get(self.api)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), TestCaseModel.objects.all().count())

    def test_get_test_case_detail(self):
        c.force_login(self.user)
        response = c.get(self.api + '1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['inputs'], 'fsdaf')
        self.assertEqual(data['output'], 'fdsjfkl')

    def test_get_test_case_detail_anon(self):
        response = c.get(self.api + '1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['inputs'], 'fsdaf')
        self.assertEqual(data['output'], 'fdsjfkl')
