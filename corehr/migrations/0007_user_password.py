# Generated by Django 4.2.4 on 2023-09-08 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corehr', '0006_attendancelogs_week_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.TextField(null=True),
        ),
    ]
