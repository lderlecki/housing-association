# Generated by Django 3.0.7 on 2020-06-10 15:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0005_auto_20200610_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='no_residents',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]