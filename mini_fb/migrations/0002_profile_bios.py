# Generated by Django 5.1.5 on 2025-02-20 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mini_fb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bios',
            field=models.TextField(blank=True),
        ),
    ]
