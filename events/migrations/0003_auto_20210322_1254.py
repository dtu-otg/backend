# Generated by Django 3.1.7 on 2021-03-22 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_registrationevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=9, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=9, max_digits=15, null=True),
        ),
    ]
