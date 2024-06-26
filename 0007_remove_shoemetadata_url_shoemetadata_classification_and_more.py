# Generated by Django 5.0.4 on 2024-06-08 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0006_remove_shoedominantcolor_shoe_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoemetadata',
            name='url',
        ),
        migrations.AddField(
            model_name='shoemetadata',
            name='classification',
            field=models.CharField(default='Unknown', max_length=30),
        ),
        migrations.CreateModel(
            name='ShoeClassification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boots_confidence', models.FloatField()),
                ('flip_flops_confidence', models.FloatField()),
                ('loafers_confidence', models.FloatField()),
                ('sandals_confidence', models.FloatField()),
                ('sneakers_confidence', models.FloatField()),
                ('soccer_shoes_confidence', models.FloatField()),
                ('shoe_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluate.shoeimage')),
            ],
        ),
    ]
