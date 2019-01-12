from scheduler.models import Timeslot, Room, Panelist, Panel, Experience, Conference

from django.db.models import Count, Lookup, Q

def schedule(conference):
    with open("schedule.tsv", "w") as text_file:
        row = "Day\t" + "Time\t"
        for room in [x.name for x in conference.rooms.order_by('id')]:
            row += room + "\t"
        row += "\n"
        text_file.write(row)

        for slot in Timeslot.objects.filter(conference=conference):
            row = slot.get_day_display() + "\t" + slot.time
            for room in conference.rooms.order_by('id'):
                row += "\t"
                panel = room.panels.filter(timeslot=slot).first()
                if panel:
                    row += "Title: " + panel.title
                    if panel.description:
                        description = panel.description
                        description.replace('\n', ' ').replace('\r', '')
                        row += " Description: " + str(panel.description)
                    row += " Panelists: "
                    if panel.moderator:
                       row += str(panel.moderator) + " (M)"
                    panelists = [p.badge_name for p in panel.final_panelists.all()]
                    for panelist in panelists:
                        row += ", " + panelist
            row += "\n"
            text_file.write(row)
        text_file.close()


def panelists(conference):
    with open("panelists.tsv", "w") as text_file:
        row = "Badge Name\t" + "Email\n"
        text_file.write(row)
        for panelist in Panelist.objects.filter(conference=conference):
            row = panelist.badge_name + "\t" + panelist.email + "\t"
            row += "\n"
            text_file.write(row)
        text_file.close()

def individual_schedules(conference):
    with open("individual_schedules.txt", "w") as text_file:
        for panelist in Panelist.objects.all():
            text_file.write(panelist.badge_name + "\n")
            text_file.write("Your Scedule:\n")
            allpanels = Panel.objects.filter(
                Q(moderator=panelist) | Q(final_panelists=panelist)
                ).distinct(
                ).order_by("timeslot")
            for panel in allpanels:
                text_file.write(panel.title + "\n")
                text_file.write(panel.timeslot.day + " " + panel.timeslot.time +", " + panel.room.name +"\n")   
            text_file.write("-------------\n\n\n")
    text_file.close()


def individual_schedule_emails(message=''):
    """
    Pass in the body of your panelist email as 'message' to get a
    fully-generated email that's ready to copy and paste.
    TODO: build mail-sending into the app.
    """

    with open("schedule_emails.txt", "w") as text_file:
        for panelist in Panelist.objects.all():
            text_file.write(panelist.email + "\n")
            text_file.write("Your ConFusion Panel Schedule" + "\n")
            text_file.write("Dear " + panelist.badge_name + ",\n")
            text_file.write(message)
            text_file.write("Your Scedule:\n\n")
            allpanels = Panel.objects.filter(
                Q(moderator=panelist) | Q(final_panelists=panelist)
                ).distinct(
                ).order_by("timeslot")
            for panel in allpanels:
                text_file.write(panel.title + "\n")
                text_file.write(panel.timeslot.day + " " + panel.timeslot.time +", " + panel.room.name +"\n")
                if panel.description:
                    text_file.write(panel.description + "\n")
                if panel.moderator:
                    text_file.write("panelists: " + panel.moderator.badge_name + " (M), ")
                for p in panel.final_panelists.all():
                    text_file.write(p.badge_name + ", ")
                text_file.write("\n\n")    
            text_file.write("-------------\n\n\n")
    text_file.close()