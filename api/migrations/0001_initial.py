# Generated by Django 4.0b1 on 2021-11-04 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checker_function', models.TextField(blank=True, null=True)),
                ('checker_func_lang', models.CharField(blank=True, choices=[('c_cpp', 'C/C++'), ('python', 'Python')], max_length=20, null=True)),
                ('correct_code', models.TextField(blank=True, null=True)),
                ('correct_lang', models.CharField(blank=True, choices=[('c_cpp', 'C/C++'), ('python', 'Python')], max_length=20, null=True)),
                ('description', models.TextField()),
                ('difficulty', models.IntegerField(default=1500)),
                ('example_number', models.IntegerField(default=1)),
                ('hidden_till', models.DateTimeField(default=django.utils.timezone.now)),
                ('input_terms', models.TextField()),
                ('memory_limit', models.IntegerField(default=256)),
                ('notice', models.TextField(blank=True, null=True)),
                ('output_terms', models.TextField()),
                ('time_limit', models.IntegerField(default=1)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ['difficulty', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Tutorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('hidden_till', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('contest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.contest')),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inputs', models.TextField()),
                ('output', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.problem')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('language', models.CharField(choices=[('c_cpp', 'C/C++'), ('python', 'Python')], max_length=10)),
                ('verdict', models.CharField(default='PJ', max_length=5)),
                ('details', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('contest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.contest')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='ContestProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem_char', models.CharField(default='A', max_length=3)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.contest')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.problem')),
            ],
            options={
                'ordering': ('problem_char',),
            },
        ),
        migrations.AddField(
            model_name='contest',
            name='problems',
            field=models.ManyToManyField(through='api.ContestProblem', to='api.Problem'),
        ),
        migrations.AddField(
            model_name='contest',
            name='testers',
            field=models.ManyToManyField(blank=True, related_name='contest_tester_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contest',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user'),
        ),
        migrations.AddField(
            model_name='contest',
            name='writers',
            field=models.ManyToManyField(blank=True, related_name='contest_writer_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.comment')),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.problem')),
                ('tutorial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.tutorial')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
