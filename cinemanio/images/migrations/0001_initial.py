# Generated by Django 2.0.1 on 2018-05-19 14:35

from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveIntegerField(choices=[(1, 'Poster'), (2, 'Photo')], db_index=True, null=True, verbose_name='Type')),
                ('original', sorl.thumbnail.fields.ImageField(upload_to='images', verbose_name='Original')),
                ('source', models.CharField(default='', max_length=100, verbose_name='Source')),
                ('source_type', models.CharField(choices=[('kinopoisk', 'kinopoisk'), ('wikicommons', 'wikicommons')], max_length=20, null=True, verbose_name='Type of source')),
                ('source_id', models.CharField(max_length=300, null=True, verbose_name='Source ID')),
            ],
            options={
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
                'ordering': ('-id',),
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='ImageLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='images.Image')),
            ],
            options={
                'verbose_name': 'image link',
                'verbose_name_plural': 'image links',
                'get_latest_by': 'id',
            },
        ),
        migrations.AlterUniqueTogether(
            name='image',
            unique_together={('source_type', 'source_id')},
        ),
        migrations.AlterUniqueTogether(
            name='imagelink',
            unique_together={('image', 'content_type', 'object_id')},
        ),
    ]