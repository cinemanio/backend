# Generated by Django 2.0.1 on 2018-02-26 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("core", "0005_auto_20180226_0222")]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="code",
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name="Code"),
        )
    ]
