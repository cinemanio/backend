# Generated by Django 2.0.8 on 2018-09-19 21:17

import cinemanio.core.models.person
from django.db import migrations, models
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_person_roles'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cast',
            options={'get_latest_by': 'id', 'ordering': ('role_id', 'id'), 'verbose_name': 'cast', 'verbose_name_plural': 'cast'},
        ),
        migrations.AddField(
            model_name='movie',
            name='title_original',
            field=models.CharField(default='', max_length=200, verbose_name='Title original'),
        ),
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=enumfields.fields.EnumIntegerField(db_index=True, enum=cinemanio.core.models.person.Gender, null=True, verbose_name='Gender'),
        ),
    ]