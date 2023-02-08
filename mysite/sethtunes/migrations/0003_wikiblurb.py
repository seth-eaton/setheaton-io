# Generated by Django 4.1.5 on 2023-02-08 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sethtunes', '0002_album_explicit'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiBlurb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('summary', models.CharField(max_length=10000)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sethtunes.artist')),
            ],
        ),
    ]
