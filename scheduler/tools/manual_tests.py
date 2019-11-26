from scheduler.models import Conference, Room, Panelist, Panel
from django.db.models import Q

import datetime

from .new_scheduler import get_hour_list

def room_integrity_check(con):
    total_dupes = 0
    for room in Room.objects.filter(conference=con):
        for panel in room.panels.all():
            dupes = 0
            if panel.start_time:
                dupes = Panel.objects.filter(
                    room=room,
                    start_time__lte=panel.start_time,
                    end_time__gte=panel.start_time).count()
            if dupes > 1:
                total_dupes += 1
                print(room, "is double-booked at", panel.start_time)
    return total_dupes


def open_rooms_check(con):
    days = con.days.all()
    hours = []
    for day in days:
        hours += get_hour_list(day)

    rooms = Room.objects.filter(conference=con,
        category__in=[Room.PANEL, Room.READING])

    for hour in hours:
        for room in rooms:
            if not room.panels.filter(
                start_time__lte=hour, end_time__gte=hour).exists():
                print(room.name, "is open at", hour)



def panelist_integrity_check(con):
    total_dupes = 0
    for panelist in Panelist.objects.filter(conference=con):
        # double booking checker
        for panel in panelist.panels.filter(start_time__isnull=False):
            dupes = panelist.panels.filter(
                start_time__lte=panel.start_time,
                end_time__gte=panel.start_time).count()
            if dupes > 1:
                total_dupes +=1
                print(panelist, "is double-booked at", panel.start_time)
            mdupes = panelist.moderating.filter(
                start_time__lte=panel.start_time,
                end_time__gte=panel.start_time)
            if mdupes.count() > 0:
                total_dupes += 1
                print(panelist, "is double-booked at", panel.start_time)
        for panel in panelist.moderating.filter(start_time__isnull=False):
            dupes = panelist.moderating.filter(
                start_time__lte=panel.start_time,
                end_time__gte=panel.start_time).count()
            if dupes > 1:
                total_dupes += 1
                print(panelist, "is double-booked at", panel.start_time)
        # break checker
        for panel in Panel.objects.filter(
            Q(moderator=panelist) | Q(final_panelists=panelist),
                start_time__isnull=False):
            recent_panel_count = 0
            max_on = datetime.timedelta(hours=panelist.inarow)
            start_window = panel.start_time - max_on
            recent_panel_count = panelist.panels.filter(
                end_time__gte=start_window,
                end_time__lte=panel.start_time).count()
            recent_panel_count += panelist.moderating.filter(
                end_time__gte=start_window,
                end_time__lte=panel.start_time).count()
            if recent_panel_count >= panelist.inarow:
                total_dupes +=1
                print(panelist, "needs a break at", panel.start_time)
    return total_dupes



