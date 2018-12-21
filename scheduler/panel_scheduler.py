
from scheduler.models import Timeslot, Room, Panelist, Panel, Experience

from django.db.models import Count, Lookup, Q

from random import randint

def export_schedule():
    with open("schedule.tsv", "w") as text_file:
        for slot in Timeslot.objects.all():
            row = str(slot)
            for panel in slot.panels.all():
                row += "\t" + panel.title + " Panelists:"
                panelists = [p.badge_name for p in panel.final_panelists.all()]
                for panelist in panelists:
                    row += " " + panelist
            row += "\n"
            text_file.write(row)
        text_file.close()
            

def randomize_panel(available_panels):
    random_index = randint(0, len(available_panels) - 1 )
    return available_panels[random_index]

def check_bench(potential_panels, need_break):

    available_panels = []
    for panel in potential_panels:
        bench = [x for x in panel.interested_panelists.all() if x not in need_break]
        if len(bench) > 2 or panel.interested_panelists.count() < 3:
            available_panels.append(panel)
    return available_panels

def get_small_panels_first(conference, exclusions, need_break, slotted_panels):

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

def get_compatible_panels(slotted_panels, available_panels2, tracks, need_break):
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
                                   id__in=on_break_ids).count()

    compatible_panels = []
    for panel in available_panels2:
        if panel.panelists_locked:
            compatible_panels.append(panel)
            continue
        panelists2 = panel.interested_panelists.exclude(id__in=on_break_ids)
        if existing_panelists + panelists2.count() >= (tracks - locked) * 5:
            compatible_panels.append(panel)
    return compatible_panels


def add_a_compatible_panel(conference, slotted_panels, available_panels1,
                            need_break, exclusions, tracks):
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
        if timeslot.panels.count() >= timeslot.tracks:
            print(timeslot, " is full. Skipping.")
            continue
        print("scheduling ", timeslot)


        slotted_panels = list(timeslot.panels.all())
        need_break= get_break_needed(timeslot)
        exclusions = Q(required_panelists__in=need_break)
        exclusions |= Q(required_panelists__panels__in=slotted_panels)

        available_panels1 = get_small_panels_first(conference,
            exclusions, need_break, slotted_panels)
        if not slotted_panels:
            # Let's try to put small panels in slot 1

            if not available_panels1:
                Print("I couldn't schedule a first panel for this slot.")
                continue

            slotted_panels.append(randomize_panel(available_panels1))

        for track in range(len(slotted_panels), timeslot.tracks + 1):
            for panel in slotted_panels:
                exclusions |= Q(
                    required_panelists__in=panel.required_panelists.all())
                exclusions |= Q(
                    final_panelists__in=panel.required_panelists.all())

            #need to regen available panels 1
            slotted_panels = add_a_compatible_panel(conference,
                slotted_panels, available_panels1, need_break,
                exclusions, timeslot.tracks)

            if len(slotted_panels) < track + 1:
                print("Nothing else fits in this slot. Moving on.")
                break

        for panel in slotted_panels:
            panel.timeslot = timeslot
            if not panel.room:
                rooms = Room.objects.filter(conference=conference,
                    category=Room.PANEL).exclude(panels__timeslot=timeslot)
                panel.room = rooms.first()
            panel.save()

        print(timeslot, "scheduled. Let's add some panelists.")

        for panel in slotted_panels:
            for panelist in panel.required_panelists.all():
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
                            Q(num_moderating__gte=2) |
                            Q(num_scheduled__gte=5)
                        ).order_by(
                        'num_interested', 'num_scheduled').first()
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

