# Generated by Django 2.0.3 on 2018-03-21 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitfinex_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='count',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='last_updated',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='actual_time',
            field=models.BigIntegerField(),
        ),
    ]