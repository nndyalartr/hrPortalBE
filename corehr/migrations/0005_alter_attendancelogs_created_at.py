# Generated by Django 4.2.4 on 2023-09-07 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corehr', '0004_attendancelogs_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendancelogs',
            name='created_at',
            field=models.DateField(null=True),
        ),
    ]
