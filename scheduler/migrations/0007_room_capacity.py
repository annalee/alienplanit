# Generated by Django 2.1.4 on 2018-12-18 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0006_panel_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='capacity',
            field=models.IntegerField(default=200, help_text='Audience capacity.'),
            preserve_default=False,
        ),
    ]
