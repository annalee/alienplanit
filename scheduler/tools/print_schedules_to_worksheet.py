from openpyxl import Workbook
from openpyxl.styles import Alignment
from string import ascii_uppercase

from django.db.models import Q

from scheduler.models import Room, Panelist, Panel, Track, Conference


def all_schedules(con):
    workbook = Workbook()
    worksheet = workbook.active

    header_row = ['Name', 'Email', 'Schedule']
    for header in header_row:
        cellid = ascii_uppercase[header_row.index(header)] + str(1)
        worksheet[cellid] = header

    rowid = 2
    for panelist in Panelist.objects.filter(
        conference=con).exclude(panels=None, moderating=None):

        panels = panelist.panels.all().union(
                    panelist.moderating.all()).order_by('start_time')

        schedule = ""
        for p in panels:
            panelists = ', '.join(
                [x.program_name for x in p.final_panelists.all()])
            moderator = ''
            if p.moderator:
                moderator = p.moderator + ' (m), '
            panelstring = "{}\n{}\n{}{}\n\n".format(
                p.title, p.description, p.moderator, panelists)
            schedule += panelstring


        worksheet['A{}'.format(rowid)] = panelist.program_name
        worksheet['B{}'.format(rowid)] = panelist.email
        worksheet['C{}'.format(rowid)] = schedule
        worksheet['C{}'.format(rowid)].alignment = Alignment(wrapText=True)

        rowid += 1

    workbook.save("{} schedule.xlsx".format(con.slug))

