# Generated by Django 2.1.4 on 2018-12-16 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_auto_20181215_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='panel',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
