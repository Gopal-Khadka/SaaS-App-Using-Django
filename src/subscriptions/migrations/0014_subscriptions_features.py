# Generated by Django 5.0.9 on 2024-11-30 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0013_alter_subscriptionprice_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptions',
            name='features',
            field=models.TextField(blank=True, help_text='Features for plan pricing separated by newline', null=True),
        ),
    ]