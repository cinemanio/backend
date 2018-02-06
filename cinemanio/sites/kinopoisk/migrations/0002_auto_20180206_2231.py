# Generated by Django 2.0.1 on 2018-02-06 22:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180206_1854'),
        ('kinopoisk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KinopoiskCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True, unique=True, verbose_name='Kinopoisk name')),
                ('country', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kinopoisk', to='core.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KinopoiskGenre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True, unique=True, verbose_name='Kinopoisk name')),
                ('genre', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kinopoisk', to='core.Genre')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='kinopoiskmovie',
            name='votes',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Kinopoisk votes number'),
        ),
    ]
