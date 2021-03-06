# Generated by Django 2.2.3 on 2019-07-31 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0021_auto_20181224_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='panelist',
            name='invite_again',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='panelist',
            name='signing_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelist',
            name='staff_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
