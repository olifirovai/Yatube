# Generated by Django 2.2.6 on 2020-05-30 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20200530_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='follow',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='beginning_following_date'),
        ),
    ]
