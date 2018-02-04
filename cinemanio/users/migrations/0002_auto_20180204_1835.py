# Generated by Django 2.0.1 on 2018-02-04 18:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('relations', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='familiar_movies',
            field=models.ManyToManyField(related_name='relations_users', through='relations.MovieRelation', to='core.Movie', verbose_name='Relations'),
        ),
        migrations.AddField(
            model_name='user',
            name='familiar_persons',
            field=models.ManyToManyField(related_name='relations_users', through='relations.PersonRelation', to='core.Person', verbose_name='Relations'),
        ),
        migrations.AddField(
            model_name='user',
            name='familiar_users_back',
            field=models.ManyToManyField(related_name='familiar_users', through='relations.UserRelation', to=settings.AUTH_USER_MODEL, verbose_name='Relations'),
        ),
    ]
