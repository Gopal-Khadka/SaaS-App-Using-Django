# Generated by Django 5.0.9 on 2024-11-30 01:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0011_alter_subscriptionprice_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptions',
            options={'ordering': ['order', 'featured', '-updated'], 'permissions': [('advanced', 'Advanced perm'), ('pro', 'Pro perm'), ('basic', 'Basic perm'), ('basic_ai', 'Basic AI perm')], 'verbose_name': 'Subscription', 'verbose_name_plural': 'Subscriptions'},
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='featured',
            field=models.BooleanField(default=True, help_text='Featured on Django pricing page'),
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='order',
            field=models.IntegerField(default=-1, help_text='Ordering on Django Pricing Page'),
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]