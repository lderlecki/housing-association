# Generated by Django 3.0.7 on 2020-06-13 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_apartment'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_is_active',
            field=models.BooleanField(default=False),
        ),
    ]
