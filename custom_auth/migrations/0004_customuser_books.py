# Generated by Django 4.2.6 on 2023-10-19 07:09

from django.db import migrations
import django_jsonform.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('custom_auth', '0003_remove_customuser_books'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='books',
            field=django_jsonform.models.fields.JSONField(default=[]),
        ),
    ]
