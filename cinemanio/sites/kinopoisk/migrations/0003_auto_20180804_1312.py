# Generated by Django 2.0.8 on 2018-08-04 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinopoisk', '0002_auto_20180206_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='kinopoiskmovie',
            name='synced_at',
            field=models.DateTimeField(db_index=True, null=True, verbose_name='Synced at'),
        ),
        migrations.AddField(
            model_name='kinopoiskperson',
            name='synced_at',
            field=models.DateTimeField(db_index=True, null=True, verbose_name='Synced at'),
        ),
    ]
