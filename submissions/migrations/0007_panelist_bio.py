# Generated by Django 2.2.3 on 2019-07-18 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0006_panelist_staff_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='panelist',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
    ]