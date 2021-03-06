# Generated by Django 2.2.4 on 2019-09-30 18:14

from django.db import migrations

def migrate_protrack(apps, schema_editor):
    Panel = apps.get_model('scheduler', 'Panel')
    Track = apps.get_model('scheduler', 'Track')
    Conference = apps.get_model('scheduler', 'Conference')

    for con in Conference.objects.all():
        protrack, created = Track.objects.get_or_create(
            slug='pro', name='Pro Track', conference=con)

    for panel in Panel.objects.filter(pro_track=True):
        pro = Track.objects.get(slug='pro', conference=panel.conference)
        panel.tracks.add(pro)
        panel.save()




class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0024_auto_20190930_1836'),
    ]

    operations = [
        migrations.RunPython(migrate_protrack),
    ]
