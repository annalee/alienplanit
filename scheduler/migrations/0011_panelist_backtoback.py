# Generated by Django 2.1.4 on 2018-12-19 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0010_room_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='panelist',
            name='backtoback',
            field=models.IntegerField(default=2, help_text='Number of panels this person can do in a row.'),
        ),
    ]