# Generated by Django 3.1.6 on 2021-05-14 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apnea_detection', '0004_auto_20210514_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='normalization',
            name='scale_factor_high',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='normalization',
            name='scale_factor_low',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='normalization',
            name='slope_threshold',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='setup',
            name='excerpt',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
