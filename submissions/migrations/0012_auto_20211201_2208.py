# Generated by Django 2.2.4 on 2021-12-01 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0011_auto_20211201_2205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='panel',
            old_name='con_fk',
            new_name='conference',
        ),
        migrations.RenameField(
            model_name='panelist',
            old_name='con_fk',
            new_name='conference',
        ),
        migrations.RenameField(
            model_name='textblock',
            old_name='con_fk',
            new_name='conference',
        ),
    ]
