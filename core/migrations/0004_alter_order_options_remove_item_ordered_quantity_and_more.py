# Generated by Django 4.2.6 on 2023-10-17 19:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_item_current_quantity_alter_item_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['bill_number']},
        ),
        migrations.RemoveField(
            model_name='item',
            name='ordered_quantity',
        ),
        migrations.AddField(
            model_name='order',
            name='son_papdi_1000',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, "Quantity can't be negative.")]),
        ),
    ]
