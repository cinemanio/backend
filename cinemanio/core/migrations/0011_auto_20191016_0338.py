# Generated by Django 2.1.8 on 2019-10-16 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20191011_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cast',
            name='name',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Role name'),
        ),
        migrations.AlterField(
            model_name='cast',
            name='name_en',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Role name'),
        ),
        migrations.AlterField(
            model_name='cast',
            name='name_ru',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='Role name'),
        ),
    ]
