# Generated by Django 5.2 on 2025-04-17 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("study", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tutorclass",
            name="duration",
            field=models.IntegerField(
                choices=[(30, "30분"), (60, "60분")], db_index=True
            ),
        ),
    ]
