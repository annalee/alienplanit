# Generated by Django 2.1.4 on 2018-12-19 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0012_auto_20181219_0234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='panel',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='panels', to='scheduler.Room'),
        ),
    ]
