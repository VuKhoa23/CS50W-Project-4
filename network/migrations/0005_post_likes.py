# Generated by Django 4.2.3 on 2023-07-30 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]
