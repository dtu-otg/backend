# Generated by Django 3.1.7 on 2021-03-31 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_remove_user_dtu_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteOnly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=255, unique=True)),
                ('otp', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
