
from scheduler.models import Timeslot, Room, Panelist, Panel, Experience, Conference

from django.db.models import Count, Lookup, Q

from random import randint

def export_schedule(conference):
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

def export_panelists(conference):
    with open("panelists.tsv", "w") as text_file:
        row = "Badge Name\t" + "Email\n"
        text_file.write(row)
        for panelist in Panelist.objects.filter(conference=conference):
            row = panelist.badge_name + "\t" + panelist.email + "\t"
            row += "\n"
            text_file.write(row)
        text_file.close()

def export_individual_schedule(conference):
    with open("individual_schedules.tsv", "w") as text_file:
        row = "Panelist\t" + "Email\t" + "Moderating\t" + "Panels\t"
        text_file.write(row)
        for panelist in Panelist.objects.all():
            row = panelist.badge_name + "\t"
            row += panelist.email + "\t"
            moderating = ""
            panels = ""
            for panel in panelist.moderating.all():
                moderating += str(panel.timeslot) + ' ' + str(panel.room.name) + ' ' + panel.title + ", "
            for panel in panelist.panels.all():
                panels += str(panel.timeslot) + ' ' + str(panel.room.name) + ' ' + panel.title + ", "
            row += moderating + "\t"
            row += panels + "\t"
            row += "\n"
            text_file.write(row)
        text_file.close()


def test_duplicated_schedules(conference):
    panelists = Panelist.objects.all()
    for panelist in panelists:
        alltimes = [x.timeslot for x in panelist.panels.filter(conference=conference)]
        alltimes += [x.timeslot for x in panelist.moderating.filter(conference=conference)]
        deduplicated = set(alltimes)
        if len(deduplicated) < len(alltimes):
            print(panelist.badge_name, "is double-booked.")
    print("Done!")


def randomize_panel(available_panels):
    random_index = randint(0, len(available_panels) - 1 )
    return available_panels[random_index]

def check_bench(potential_panels, need_break):

    available_panels = []
    for panel in potential_panels:
        bench = [x for x in panel.interested_panelists.all(
                    ) if x not in need_break]
        if len(bench) > 2 or panel.interested_panelists.count() < 3:
            available_panels.append(panel)
    return available_panels

def get_small_panels_first(conference, exclusions, need_break,
                            slotted_panels, booked_rooms):

    potential_panels = Panel.objects.annotate(
            num_interested = Count('interested_panelists')
            ).filter(conference=conference,
                     timeslot__isnull=True,
                     num_interested__lt=6
            ).exclude(exclusions)

    available_panels = check_bench(potential_panels, need_break)

    # If no small panel fits...
    if not available_panels:
        potential_panels = Panel.objects.filter(
            conference=conference, timeslot__isnull=True).exclude(exclusions)

        available_panels = check_bench(potential_panels, need_break)

    return available_panels

def get_compatible_panels(slotted_panels, available_panels2,
                            tracks, need_break):
    # we need to make sure there isn't too much overlap in interested panelists
    # to schedule two panels side-by-side. Excluding locked panels because
    # they're weird.
    existing_panelists = []
    locked = 0
    on_break_ids = [x.id for x in need_break]

    for panel in slotted_panels:
        if panel.panelists_locked:
            locked +=1
            continue
        existing_panelists += panel.interested_panelists.exclude(
                                   id__in=on_break_ids)

    compatible_panels = []
    for panel in available_panels2:
        if panel.panelists_locked:
            compatible_panels.append(panel)
            continue
        panelists2 = panel.interested_panelists.exclude(id__in=on_break_ids)
        unlocked = tracks - locked
        if len(existing_panelists) + panelists2.count() >= unlocked * 5:
            compatible_panels.append(panel)
    return compatible_panels


def add_a_compatible_panel(conference, slotted_panels, available_panels1,
                            need_break, exclusions, tracks, booked_rooms):
    smallpanel = False
    for panel in slotted_panels:
        if panel.interested_panelists.count() < 6:
            smallpanel = True
            break

    # only one small panel per slot.
    if smallpanel:
        available_panels2 = Panel.objects.annotate(
            num_interested = Count('interested_panelists')).filter(
            conference=conference, timeslot__isnull=True, num_interested__gt=5
            ).exclude(exclusions)
    else:
        available_panels2 = Panel.objects.filter(conference=conference,
            timeslot__isnull=True).exclude(exclusions)

    compatible_panels = get_compatible_panels(slotted_panels, available_panels2,
                                              tracks, need_break)

    if not compatible_panels:
        for panel in available_panels1:
            slotted_panels[0] = panel
            available_panels2 = Panel.objects.filter(conference=conference,
                timeslot__isnull=True).exclude(exclusions)
            compatible_panels = get_compatible_panels(slotted_panels,
                                                      available_panels2,
                                                      tracks, need_break)
            if compatible_panels:
                slotted_panels.append(randomize_panel(compatible_panels))
                return slotted_panels
        return slotted_panels
    slotted_panels.append(randomize_panel(compatible_panels))
    return slotted_panels

def get_break_needed(timeslot):
    need_break = []
    last_hour = timeslot.previous_slot
    if last_hour:
        last_hour_panels = Panel.objects.filter(timeslot=last_hour)
        last_hour_panelists = Panelist.objects.filter(
                                               panels__in=last_hour_panels)

        for person in last_hour_panelists:
            if person.inarow == 1:
                need_break.append(person)
                continue
            hour = last_hour.previous_slot
            if not hour:
                continue
                # We're reached the beginning of the day before hitting
                # the panelist's limit.
            for x in range(1, person.inarow):
                working = person.panels.filter(timeslot=hour)
                if not working:
                    #They took a break
                    break
                if x == person.inarow - 1:
                    # this is the last hour in their limit and they've worked
                    # all of them, so they need a break.
                    need_break.append(person)
                hour = hour.previous_slot

    return need_break


def schedule_panels(conference):
    for timeslot in Timeslot.objects.filter(conference=conference):
        #skip already-full slots
        if timeslot.panels.filter(room__category=Room.PANEL).count() >= timeslot.tracks:
            print(timeslot, " is full. Skipping.")
            continue
        print("scheduling ", timeslot)


        slotted_panels = list(timeslot.panels.all())
        need_break= get_break_needed(timeslot)
        booked_rooms = Room.objects.filter(conference=conference, panels__timeslot=timeslot)
        exclusions  = Q(room__in=booked_rooms)
        exclusions |= Q(required_panelists__in=need_break)
        exclusions |= Q(required_panelists__panels__in=slotted_panels)
        exclusions |= Q(final_panelists__in=need_break)
        exclusions |= Q(final_panelists__panels__in=slotted_panels)
        exclusions |= Q(moderator__panels__in=slotted_panels)

        available_panels1 = get_small_panels_first(conference,
            exclusions, need_break, slotted_panels, booked_rooms)
        if not slotted_panels:
            # Let's try to put small panels in slot 1

            if not available_panels1:
                Print("I couldn't schedule a first panel for this slot.")
                continue

            slotted_panels.append(randomize_panel(available_panels1))

        for track in range(len(slotted_panels), timeslot.tracks +1):
            for panel in slotted_panels:
                exclusions |= Q(
                    required_panelists__in=panel.required_panelists.all())
                exclusions |= Q(
                    final_panelists__in=panel.required_panelists.all())
                exclusions |= Q(moderator=panel.moderator)

            #need to regen available panels 1
            slotted_panels = add_a_compatible_panel(conference,
                slotted_panels, available_panels1, need_break,
                exclusions, timeslot.tracks, booked_rooms)

            if len(slotted_panels) < track + 1:
                print("Nothing else fits in this slot. Moving on.")
                break

        # sort slotted_panels by who's already got a room and assign those first
        slotted1 = [x for x in slotted_panels if x.room]
        slotted2 = [x for x in slotted_panels if x not in slotted1]
        slotted_panels = slotted1 + slotted2       

        for panel in slotted_panels:
            panel.timeslot = timeslot

            if not panel.room:
                booked_rooms = Room.objects.filter(conference=conference, panels__timeslot=timeslot)
                # print(str(booked_rooms.all()), " are already full.")
                rooms = Room.objects.filter(conference=conference,
                    category=Room.PANEL).exclude(panels__timeslot=timeslot)
                print("booking ", rooms.first())
                panel.room = rooms.first()
            panel.save()

        print(timeslot, "scheduled. Let's add some panelists.")

        for panel in slotted_panels:
            for panelist in panel.required_panelists.all():
                if panel not in panelist.moderating.all():
                    panel.final_panelists.add(panelist)
            if not panel.panelists_locked:
                need_break_ids = [x.id for x in need_break]
                bench_ids = [x.id for x in panel.interested_panelists.all(
                                ) if x not in need_break]

                if not panel.moderator:
                    panel.moderator = panel.interested_moderators.annotate(
                        num_interested=Count('interested_mod'),
                        num_scheduled=Count('panels')+Count('moderating'),
                        num_moderating=Count('moderating')).exclude(
                            Q(id__in=need_break_ids) |
                            Q(num_moderating__gte=3) |
                            Q(num_scheduled__gte=5)
                        ).order_by(
                        'num_moderating', 'num_scheduled', 'num_interested',).first()
                    if not panel.moderator:
                        print("Couldn't find a moderator for", panel.title)
                total = panel.final_panelists.count()
                if total < 4:
                    remaining = 4 - total
                    chosen = panel.interested_panelists.annotate(
                        num_interested=Count('interested'),
                        num_scheduled=Count('panels') +Count('moderating')
                        ).exclude(Q(id__in=need_break_ids) |
                                  Q(moderating=panel) |
                                  Q(num_scheduled__gte=5)
                        ).order_by(
                            'num_interested', 'num_scheduled')[:remaining]
                    for panelist in chosen:
                        panelist.panels.add(panel)
                        panelist.save()
            panel.save()


    return "Done!"

def schedule_readings(conference, room):
    reading_ids = []
    for timeslot in Timeslot.objects.filter(conference=conference,
                                         reading_slots__gte=1):
        need_break_ids = [x.id for x in get_break_needed(timeslot)]
        readers = Panelist.objects.filter(
            reading_requested=True).exclude(
            id__in=reading_ids).exclude(
            id__in=need_break_ids)[:3]

        title = "Reading: "
        for reader in readers:
            title += reader.badge_name
            title += ", "
        groupreading = Panel.objects.create(conference=conference,
                             title=title,
                             timeslot=timeslot,
                             room=room,
                             av_required=False,
                             roomsize = 25)
        groupreading.final_panelists.set(readers)
        groupreading.save()

        reading_ids.extend([x.id for x in readers])
        print("Scheduled", groupreading.title, "on", timeslot.day, "at", timeslot.time)