# Generated by Django 4.0b1 on 2021-11-03 02:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplify_rest_framework', '0002_demomodel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Demo',
        ),
        migrations.DeleteModel(
            name='DemoModel',
        ),
    ]
