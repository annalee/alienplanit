# Generated by Django 2.1.4 on 2018-12-18 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0008_panel_roomsize'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='panel',
            unique_together={('room', 'timeslot')},
        ),
    ]
