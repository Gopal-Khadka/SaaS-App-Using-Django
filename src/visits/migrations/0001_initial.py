# Generated by Django 5.0.9 on 2024-11-21 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PageVisits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.TextField(blank=True, null=True)),
                ('timestamp', models.TimeField(auto_now_add=True)),
            ],
        ),
    ]
