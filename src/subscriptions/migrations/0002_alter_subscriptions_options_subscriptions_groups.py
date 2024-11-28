# Generated by Django 5.0.9 on 2024-11-27 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'permissions': [('advanced', 'Advanced perm'), ('pro', 'Pro perm'), ('basic', 'Basic perm'), ('basic_ai', 'Basic AI perm')]},
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='groups',
            field=models.ManyToManyField(to='auth.group'),
        ),
    ]