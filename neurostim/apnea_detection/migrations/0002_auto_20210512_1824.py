# Generated by Django 3.1.6 on 2021-05-12 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apnea_detection', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setup',
            old_name='database',
            new_name='dataset',
        ),
        migrations.AddField(
            model_name='normalization',
            name='scale',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='normalization',
            name='norm',
            field=models.CharField(choices=[('Linear', 'linear'), ('Nonlinear', 'nonlinear')], default='Linear', max_length=20),
        ),
        migrations.AlterField(
            model_name='setup',
            name='excerpt',
            field=models.IntegerField(default=1),
        ),
    ]