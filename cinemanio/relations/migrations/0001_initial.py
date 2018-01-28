# Generated by Django 2.0.1 on 2018-01-28 02:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fav', models.BooleanField(db_index=True, default=False, verbose_name='Fav')),
                ('like', models.BooleanField(db_index=True, default=False, verbose_name='Like')),
                ('seen', models.BooleanField(db_index=True, default=False, verbose_name='Have watched')),
                ('dislike', models.BooleanField(db_index=True, default=False, verbose_name='Dislike')),
                ('want', models.BooleanField(db_index=True, default=False, verbose_name='Want to watch')),
                ('ignore', models.BooleanField(db_index=True, default=False, verbose_name="Don't want to watch")),
                ('have', models.BooleanField(db_index=True, default=False, verbose_name='Have in collection')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='core.Movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MovieRelationCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favs_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('likes_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('seens_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('dislikes_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('wants_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('ignores_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('haves_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('object', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='relations_count', to='core.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='PersonRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fav', models.BooleanField(db_index=True, default=False, verbose_name='Fav')),
                ('like', models.BooleanField(db_index=True, default=False, verbose_name='Like')),
                ('dislike', models.BooleanField(db_index=True, default=False, verbose_name='Dislike')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='core.Person')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonRelationCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favs_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('likes_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('dislikes_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('object', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='relations_count', to='core.Person')),
            ],
        ),
        migrations.CreateModel(
            name='UserRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.BooleanField(db_index=True, default=False, verbose_name='Friend')),
                ('expert', models.BooleanField(db_index=True, default=False, verbose_name='Expert')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('id',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserRelationCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movies', models.PositiveIntegerField(default=0, verbose_name='Familiar movies count')),
                ('persons', models.PositiveIntegerField(default=0, verbose_name='Familiar persons count')),
                ('friends_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('experts_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('object', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='relations_count', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userrelation',
            unique_together={('object', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='personrelation',
            unique_together={('object', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='movierelation',
            unique_together={('object', 'user')},
        ),
    ]