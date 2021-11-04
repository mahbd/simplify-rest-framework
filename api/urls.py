from django.db.models import Q
from django.urls import path, include
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from simplify_rest_framework import factories, register, ModelFactory
from simplify_rest_framework.permissions import IsOwnerOrReadOnly
from .models import ContestProblem, Contest, Problem, Comment, TestCase, Submission, Tutorial, User

factories.register(ContestProblem)
factories.register(Comment)
factories.register(Submission)
factories.register(Tutorial)


def create_user(self, validated_data):
    user = User.objects.create_user(**validated_data)
    return user


def generate_new_field_method(key):
    def get_new_field(self, instance):
        return "Mahmudul Alam"

    get_new_field.__name__ = f'get_{key}'
    return get_new_field


@register(User)
class UserFactory(ModelFactory):
    def __init__(self):
        super().__init__()
        self.fields = ["username", "first_name", "last_name", "email", "password"]
        self.write_only_fields = ["password"]
        self.create_instance = create_user


@register(Problem)
class ProblemFactory(ModelFactory):
    def __init__(self):
        super().__init__()
        self.auto_user_field = "user"
        self.readonly_fields = ["user"]
        self.permission_classes = [{'class': IsOwnerOrReadOnly, 'owner_fields': ['user']}]
        self.fields_for_owner = [
            "correct_code", "correct_lang", "description", "difficulty", "example_number", "hidden_till",
            "input_terms", "memory_limit", "notice", "output_terms", "time_limit", "title", "user", "created_at",
            {"field": "test_cases", "db_field": "testcase_set", "fields": ["inputs", "output"]}
        ]
        self.fields_for_user = ["description", "difficulty", "example_number",
                                "input_terms", "memory_limit", "notice", "output_terms", "time_limit", "title", "user",
                                {"field": "test_cases", "db_field": "testcase_set", "fields": ["inputs", "output"]}
                                ]
        self.filterset_fields = ['user', 'submission__verdict', 'submission__user']

    def get_queryset(self1, self):
        if self.request.GET.get('unsolved_problems'):
            solved_ids = [problem.id for
                          problem in Problem.objects.only('id').filter(submission__verdict='AC',
                                                                       submission__user=self.request.user)]
            return Problem.objects.exclude(id__in=solved_ids).filter(hidden_till__lt=timezone.now())
        if self.request.GET.get('test_problems'):
            q = Q(contest__writers=self.request.user) | Q(contest__testers=self.request.user)
            return Problem.objects.filter(q, contest__start_time__gt=timezone.now())
        return super().get_queryset(self)

    def get_serializer_class(self1, self):
        request = self.request
        if self.kwargs.get('pk'):
            if Problem.objects.filter(pk=self.kwargs.get('pk')).exists():
                if self.request.user == Problem.objects.filter(pk=self.kwargs.get('pk')).first().user:
                    self1.fields = self1.fields_for_owner
        elif request.method == 'POST':
            self1.fields = self1.fields_for_owner
            super().get_serializer_class(self)
        else:
            self1.fields = self1.fields_for_user
        return super().get_serializer_class(self)


@register(Contest)
class ContestFactory(ModelFactory):
    def __init__(self):
        super().__init__()
        self.auto_user_field = "user"
        self.readonly_fields = ["user"]
        self.permission_classes = [{'class': IsOwnerOrReadOnly, 'owner_fields': ['user', 'writers', 'testers']},
                                   IsAuthenticatedOrReadOnly]
        self.fields = ["description", "end_time", "start_time", "title", "user", "writers", "testers",
                       {"field": "writers_detail", "db_field": "writers", "fields": ["username", "first_name", "last_name"]}
                       ]
        self.filterset_fields = ['user', 'writers', "testers"]


@register(TestCase)
class TestCaseFactory(ModelFactory):
    def __init__(self):
        super().__init__()
        self.disabled_actions = ['update', 'partial_update']
        self.auto_user_field = "user"
        self.readonly_fields = ["user"]
        self.permission_classes = [{'class': IsOwnerOrReadOnly, 'owner_fields': ['user']}, IsAuthenticatedOrReadOnly]


urlpatterns = [
    path('', include(factories.get_urls())),
]
