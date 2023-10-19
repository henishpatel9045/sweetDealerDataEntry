# Generated by Django 4.2.6 on 2023-10-18 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_order_amount_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_number', models.IntegerField(db_index=True, unique=True)),
                ('dealer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['book_number'],
            },
        ),
    ]
