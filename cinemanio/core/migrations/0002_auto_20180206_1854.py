# Generated by Django 2.0.1 on 2018-02-06 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='imdb_id',
        ),
        migrations.RemoveField(
            model_name='genre',
            name='imdb_id',
        ),
        migrations.RemoveField(
            model_name='language',
            name='imdb_id',
        ),
    ]