# Generated by Django 3.1.7 on 2021-03-18 07:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('latitude', models.DecimalField(decimal_places=9, max_digits=15)),
                ('longitude', models.DecimalField(decimal_places=9, max_digits=15)),
                ('description', models.TextField(blank=True, max_length=300, null=True)),
                ('date_time', models.DateTimeField(blank=True, null=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('type_event', models.CharField(choices=[('1', 'University'), ('2', 'Society'), ('3', 'Social')], default='1', max_length=1)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
