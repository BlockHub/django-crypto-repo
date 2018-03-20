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
                ('count', models.IntegerField()),
                ('last_updated', models.IntegerField()),
                ('time', models.DateTimeField()),
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
                ('precision', models.CharField(default='P0', max_length=2, null=True)),
                ('frequency', models.CharField(default='F0', max_length=2, null=True)),
                ('length', models.CharField(default='25', max_length=3)),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bitfinex_app.Market')),
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
                ('actual_time', models.IntegerField()),
                ('bid', models.FloatField()),
                ('bid_size', models.FloatField()),
                ('ask', models.FloatField()),
                ('ask_size', models.FloatField()),
                ('daily_change', models.FloatField()),
                ('daily_change_percentage', models.FloatField()),
                ('last_price', models.FloatField()),
                ('volume', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('market', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bitfinex_app.Market')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='orderbook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bitfinex_app.OrderBook'),
        ),
        migrations.AlterUniqueTogether(
            name='market',
            unique_together={('tkr', 'quote')},
        ),
        migrations.AddIndex(
            model_name='ticker',
            index=models.Index(fields=['time'], name='bitfinex_ap_time_afcd9a_idx'),
        ),
    ]
