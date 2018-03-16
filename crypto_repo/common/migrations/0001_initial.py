# Generated by Django 2.0.3 on 2018-03-16 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractOrderBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy', models.BooleanField()),
                ('quantity', models.FloatField()),
                ('rate', models.FloatField()),
                ('time', models.DateTimeField()),
            ],
        ),
    ]
