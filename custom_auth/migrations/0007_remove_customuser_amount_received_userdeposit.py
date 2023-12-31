# Generated by Django 4.2.6 on 2023-11-12 06:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('custom_auth', '0006_customuser_total_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='amount_received',
        ),
        migrations.CreateModel(
            name='UserDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=0)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
