# Generated by Django 5.1.6 on 2025-04-24 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.URLField(blank=True),
        ),
    ]
