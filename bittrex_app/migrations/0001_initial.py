# Generated by Django 2.0.3 on 2018-03-20 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verbose', models.CharField(max_length=100, null=True)),
                ('tkr', models.CharField(max_length=100)),
                ('quote', models.CharField(max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('min_trade_size', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy', models.NullBooleanField()),
                ('quantity', models.FloatField()),
                ('rate', models.FloatField()),
            ],
            options={
                'get_latest_by': 'time',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bittrex_app.Market')),
            ],
            options={
                'get_latest_by': 'time',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ticker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('bid', models.FloatField()),
                ('ask', models.FloatField()),
                ('last', models.FloatField()),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bittrex_app.Market')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='orderbook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bittrex_app.OrderBook'),
        ),
        migrations.AlterUniqueTogether(
            name='market',
            unique_together={('tkr', 'quote')},
        ),
        migrations.AddIndex(
            model_name='ticker',
            index=models.Index(fields=['time'], name='bittrex_app_time_da04a9_idx'),
        ),
    ]
