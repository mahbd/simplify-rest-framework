from django.contrib import admin

from .models import ContestProblem, Contest, Problem, Comment, TestCase, Submission, Tutorial


class ContestProblemInline(admin.TabularInline):
    model = ContestProblem
    extra = 1


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    inlines = [ContestProblemInline]


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    pass


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    pass


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    pass
