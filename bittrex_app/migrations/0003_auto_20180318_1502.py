# Generated by Django 2.0.3 on 2018-03-18 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bittrex_app', '0002_auto_20180318_0620'),
    ]

    operations = [
        migrations.RenameField(
            model_name='market',
            old_name='base_currency',
            new_name='quote',
        ),
        migrations.AlterUniqueTogether(
            name='market',
            unique_together={('tkr', 'quote')},
        ),
    ]
