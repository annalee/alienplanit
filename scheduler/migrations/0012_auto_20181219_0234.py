# Generated by Django 2.1.4 on 2018-12-19 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0011_panelist_backtoback'),
    ]

    operations = [
        migrations.RenameField(
            model_name='panelist',
            old_name='backtoback',
            new_name='inarow',
        ),
    ]
