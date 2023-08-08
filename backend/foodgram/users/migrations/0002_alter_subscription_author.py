# Generated by Django 4.2.4 on 2023-08-08 12:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribed', to=settings.AUTH_USER_MODEL, verbose_name='Подписан на'),
        ),
    ]
