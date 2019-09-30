# Generated by Django 2.2.4 on 2019-09-30 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0022_auto_20190731_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='panelist',
            name='conference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='panelists', to='scheduler.Conference'),
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=280)),
                ('conference', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tracks', to='scheduler.Conference')),
            ],
        ),
        migrations.AddField(
            model_name='panel',
            name='tracks',
            field=models.ManyToManyField(blank=True, related_name='panels', to='scheduler.Track'),
        ),
        migrations.AddField(
            model_name='panelist',
            name='tracks',
            field=models.ManyToManyField(blank=True, related_name='panelists', to='scheduler.Track'),
        ),
    ]