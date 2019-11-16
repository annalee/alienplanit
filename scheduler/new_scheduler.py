import random
import datetime

from django.db.models import Count, Lookup, Q

from scheduler.models import Day, Room, Panelist, Panel, Experience, Conference, Track


def check_bench(potential_panels, need_break):

    available_panels = []
    need_break_ids = [x.id for x in need_break]
    for panel in potential_panels:
        bench = panel.interested_panelists.exclude(id__in=need_break_ids)
        if len(bench) > 2 or panel.interested_panelists.count() < 3:
            available_panels.append(panel)
    return available_panels


def get_compatible_panels(slotted_panels, potential_panels, track, need_break):
    # we need to make sure there isn't too much overlap in interested panelists
    # to schedule two panels side-by-side. For locked panels, we only count
    # required panelists, not interested.
    existing_panelists = []
    locked = 0
    on_break_ids = [x.id for x in need_break]

    for panel in slotted_panels:
        if panel.panelists_locked:
            existing_panelists += list(panel.required_panelists)
            locked += 1
        else:
            existing_panelists += list(panel.interested_panelists.exclude(
                                   id__in=on_break_ids))
    existing_ids = [x.id for x in existing_panelists]

    compatible_panels = []
    for panel in potential_panels:
        if panel.panelists_locked:
            # incompatible panels should be filtered out by exclusions
            compatible_panels.append(panel)
            continue
        interested = panel.interested_panelists.exclude(
            id__in=on_break_ids + existing_ids)
        if interested.count() >= (track.panels_this_hour - locked) * 4:
            compatible_panels.append(panel)
    return compatible_panels


def add_a_compatible_panel(conference, slotted_panels, available_panels,
                            need_break, exclusions, track):

    def get_potential_panels(conference, track, exclusions):
        return Panel.objects.filter(
            conference=conference,
            tracks=track,
            start_time__isnull=True).exclude(exclusions)

    potential_panels = get_potential_panels(conference, track, exclusions)
    compatible_panels = get_compatible_panels(
        slotted_panels, potential_panels, track, need_break)

    if compatible_panels:
        chosen = random.choice(compatible_panels)
        slotted_panels.append(chosen) 
        print("Adding", chosen.title)
    else:
        print("No compatible panels. Retrying.") 
        for panel in available_panels:
            slotted_panels[0] = panel
            potential_panels = get_potential_panels(
                                    conference, track, exclusions)
            compatible_panels = get_compatible_panels(
                                    slotted_panels, potential_panels,
                                    track, need_break)
            if compatible_panels:
                slotted_panels.append(random.choice(compatible_panels))
                return slotted_panels
        return slotted_panels
    
    return slotted_panels


def get_small_panels_first(
    conference, exclusions, need_break, track):

    potential_panels = Panel.objects.annotate(
            num_interested = Count('interested_panelists')
            ).filter(conference=conference,
                     start_time__isnull=True,
                     num_interested__lt=6,
                     tracks=track
            ).exclude(exclusions)

    available_panels = check_bench(potential_panels, need_break)

    # If no small panel fits...
    if not available_panels:
        potential_panels = Panel.objects.filter(
            conference=conference,
            start_time__isnull=True,
            tracks=track
            ).exclude(exclusions)

        available_panels = check_bench(potential_panels, need_break)

    return available_panels


def add_exclusions(panel):
    # Adds exclusions to the Q object for a newly-slotted panel.
    exclusions = Q(
        required_panelists__in=panel.required_panelists.all())
    exclusions = Q(
        required_panelists__in=panel.final_panelists.all())
    exclusions |= Q(
        final_panelists__in=panel.required_panelists.all())
    exclusions |= Q(
        final_panelists__in=panel.final_panelists.all())
    if panel.moderator:
        exclusions |= Q(
            required_panelists=panel.moderator)
        exclusions |= Q(
            moderator=panel.moderator)
        exclusions |= Q(
            final_panelists=panel.moderator)
    return exclusions

def get_will_need_break(hour, panelists):
    need_break = []
    for panelist in panelists:
        max_on = datetime.timedelta(hours=panelist.inarow)
        end_window = hour + max_on
        upcoming_panel_count = panelist.panels.filter(
            end_time__gte=hour,
            end_time__lte=end_window).count()
        upcoming_panel_count += panelist.moderating.filter(
            end_time__gte=hour,
            end_time__lte=end_window).count()
        if upcoming_panel_count == panelist.inarow:
            need_break.append(panelist)
    return need_break

def get_break_needed(hour, panelists):
    need_break = []
    for panelist in panelists:
        max_on = datetime.timedelta(hours=panelist.inarow)
        start_window = hour - max_on
        recent_panel_count = panelist.panels.filter(
            end_time__gte=start_window,
            end_time__lte=hour).count()
        recent_panel_count += panelist.moderating.filter(
            end_time__gte=start_window,
            end_time__lte=hour).count()
        if recent_panel_count == panelist.inarow:
            need_break.append(panelist)
    return need_break


def get_hour_list(day):
    # Returns a list of datetime objects containing each hour of the day
    # between start_time and end_time.
    hour = datetime.timedelta(hours=1)
    current = datetime.datetime.combine(day.day, day.start_time)
    end = datetime.datetime.combine(day.day, day.end_time) - hour

    hours = []
    while current < end:
        hours.append(current)
        current += hour
    return hours


def calculate_overlap(start1, end1, start2, end2):
    # 1 starts before or at 2's start and ends after 2 starts
    overlap = datetime.timedelta()
    if start1 <= start2 and end1 > start2:
        if end1 >= end2:
            # The day encompasses the whole track
            overlap = end2 - start2
        else:
            # The track continues past the end of the day
            overlap = end1 - start2
        return overlap.seconds % 3600 // 60
    # 2 starts before or at 1's start and ends after 1 starts
    elif start2 <= start1 and end2 > start1:
        if end2 >= end1:
            # The track encompasses the whole day
            overlap = end1 - start1
        else:
            # The day continues past the end of the track
            overlap = end2 - start1
    return overlap.total_seconds() // 3600 # total hours with no remainder


def schedule_panels(conference):
    # Get the Day objects for the conference
    tracks = conference.tracks.all()
    days = conference.days.all()
    panelists = conference.panelists.all()
    if not tracks:
        print("I can't schedule a conference without tracks.")
        return
    elif not days:
        print("I can't schedule a conference without days.")
        return
    elif not panelists:
        print("I can't schedule a conference without panelists.")
        return
    # We need to determine how many panels to schedule each hour for each track
    # to have the content evenly-spread
    panels_per_hour = {}
    for track in tracks:
        total_panels = track.panels.count()
        total_hours = 0
        for day in days:
            start = datetime.datetime.combine(day.day, day.start_time)
            end = datetime.datetime.combine(day.day, day.end_time)
            total_hours += calculate_overlap(start, end, track.start, track.end)

        # get the floor of panels per hour
        base_panels_per_hour = total_panels//total_hours

        # randomly assign which hours get the extra panel above the floor number
        # of panels per hour by assembling a deck for the hours to draw from.
        extras = int(total_panels % total_hours)
        deck = [1 for x in range(0, extras)]
        deck += [0 for x in range(extras, int(total_hours))]
        paneldeck = [x + int(base_panels_per_hour) for x in deck]
        random.shuffle(paneldeck)
        panels_per_hour[track] = paneldeck


    for day in days:
        print("Scheduling", day)
        for hour in get_hour_list(day):
            print("Scheduling", hour)
            slotted_panels = list(Panel.objects.filter(
                conference=conference,
                start_time__lte=hour,
                end_time__gt=hour,
                ).select_related('room'))
            need_break = get_break_needed(hour, panelists)
            need_break += get_will_need_break(hour, panelists)
            booked_rooms = [p.room for p in slotted_panels]
            exclusions  = Q(room__in=booked_rooms)
            exclusions |= Q(required_panelists__in=need_break)
            exclusions |= Q(final_panelists__in=need_break)
            for panel in slotted_panels:
                exclusions |= add_exclusions(panel)

            open_rooms = Room.objects.filter(
                conference=conference,
                category=Room.PANEL).exclude(
                id__in=[r.id for r in booked_rooms])

            # Check which tracks are active this hour
            tracks = tracks.filter(start__lte=hour, end__gt=hour)

            # Cycle through active tracks and slot in panels for them
            for track in tracks:
                booked = Panel.objects.filter(
                conference=conference,
                start_time__lte=hour,
                end_time__gt=hour,
                tracks=track)
                bookedcount = len(booked)
                for b in booked:
                    exclusions |= add_exclusions(panel)
                track.panels_this_hour = panels_per_hour[track].pop(0)

                if track.panels_this_hour == 0:
                    continue
                while bookedcount < track.panels_this_hour:
                    roomless = [x for x in slotted_panels if not x.room]
                    if len(roomless) >= len(open_rooms):
                        print("Out of rooms. Moving on.")
                        break
                    if not booked:
                        # Let's try to schedule a panel, starting with a small one
                        available_panels = get_small_panels_first(conference,
                            exclusions, need_break, track)

                        if available_panels:
                            panel_to_add = random.choice(available_panels)
                            slotted_panels.append(panel_to_add)
                            exclusions |= add_exclusions(panel_to_add)
                            bookedcount += 1
                            print("Adding", panel_to_add.title)
                        else:
                            print("Couldn't schedule a panel for {} Track this hour.".format(
                                track.name))
                            break
                    else:
                        potential_panels = Panel.objects.filter(
                            conference=conference,
                            start_time__isnull=True,
                            tracks=track
                            ).exclude(exclusions)

                        available_panels = check_bench(potential_panels, need_break)

                        slotted_panels = add_a_compatible_panel(conference,
                            slotted_panels, available_panels, need_break,
                            exclusions, track)
                        bookedcount += 1

            for panel in slotted_panels:
                panel.start_time = hour
                panel.end_time = hour + datetime.timedelta(minutes=50)

                if not panel.room:
                    # filtering open rooms because we may have added a panel
                    # with a room assigned.
                    open_rooms = open_rooms.exclude(panels__in=slotted_panels)
                    print("booking ", open_rooms.first())
                    panel.room = open_rooms.first()
                panel.save()


            # Regenerating slotted_panels from the db because the existing list
            # is causing panelists to get double-booked. Honestly don't under-
            # -stand how this could be a caching issue but hey.
            slotted_panels = list(Panel.objects.filter(
                conference=conference,
                start_time__lte=hour,
                end_time__gt=hour,
                ).select_related('room'))

            # putting panels with moderators first so the same mods don't get
            # booked for other panels in the slot.
            slotted_with_mod = [x for x in slotted_panels if x.moderator]
            slotted_no_mod =  [x for x in slotted_panels if not x.moderator]
            slotted_panels = slotted_with_mod + slotted_no_mod
            for panel in slotted_panels:
                for panelist in panel.required_panelists.all():
                    if panelist is not panel.moderator:
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
                                Q(moderating__in=slotted_panels) |
                                Q(panels__in=slotted_panels) |
                                Q(required_for__in=slotted_panels) |
                                # Q(id__in=[x.moderator.id for x in slotted_panels if x.moderator]) |
                                # Q(panels__id__in=[x.id for x in slotted_panels]) |
                                Q(num_moderating__gte=3) |
                                Q(num_scheduled__gte=5)
                            ).order_by(
                            'num_moderating', 'num_scheduled', 'num_interested').first()
                        if panel.moderator in panel.final_panelists.all():
                            panel.final_panelists.remove(panel.moderator)
                        if not panel.moderator:
                            print("Couldn't find a moderator for", panel.title)
                    total = panel.final_panelists.count()
                    if total < 3:
                        remaining = 3 - total
                        modids = []
                        if panel.moderator:
                            modids = [x.moderator.id for x in slotted_panels if x.moderator]
                            modids += [panel.moderator.id]
                        chosen = panel.interested_panelists.annotate(
                            num_interested=Count('interested'),
                            num_scheduled=Count('panels') + Count('moderating')
                            ).exclude(Q(id__in=need_break_ids) |
                                      Q(id__in=modids) |
                                      Q(required_for__id__in=[x.id for x in slotted_panels]) |
                                      Q(panels__id__in=[x.id for x in slotted_panels]) |
                                      Q(num_scheduled__gte=5)
                            ).order_by(
                                'num_interested', 'num_scheduled')[:remaining]
                        for panelist in chosen:
                            panelist.panels.add(panel)
                            panelist.save()
                panel.save()

    print("Couldn't schedule the following panels:")
    total = 0
    for panel in Panel.objects.filter(
        conference=conference, start_time__isnull=True).annotate(
        ipcount=Count('interested_panelists')):
        print(panel.title)
        print("Interested panelists: {}".format(panel.ipcount))
        total += 1
    print("Total:", total)
    return "Done!"

def schedule_readings(conference, room):
    reading_ids = []
    days = conference.days.all()
    panelists = Panelist.objects.filter(
        conference=conference, reading_requested=True)
    # Get the longest track and run readings during that
    tracks_by_length = []
    for track in Track.objects.filter(conference=conference):
        tracks_by_length.append((track.start - track.end, track.id))
    tracks_by_length.sort()
    reading_track = Track.objects.get(id=tracks_by_length[-1][1])

    for day in days:
        for hour in get_hour_list(day):
            if hour <= reading_track.start:
                continue
            elif hour >= reading_track.end:
                return "Done."
            slotted_panels = Panel.objects.filter(
                conference=conference,
                start_time__lte=hour,
                end_time__gt=hour)
            need_break_ids = [x.id for x in get_break_needed(hour, panelists)]
            need_break_ids += [x.id for x in get_will_need_break(hour, panelists)]
            readers = panelists.exclude(
                Q(id__in=reading_ids) |
                Q(id__in=need_break_ids) |
                Q(panels__in=slotted_panels) |
                Q(moderating__in=slotted_panels)
                )[:3]

            title = "Reading: "
            for reader in readers:
                title += reader.program_name
                title += ", "
            groupreading = Panel.objects.create(conference=conference,
                                 title=title,
                                 start_time=hour,
                                 end_time=hour + datetime.timedelta(minutes=50),
                                 room=room,
                                 av_required=False,
                                 roomsize = 25)
            groupreading.final_panelists.set(readers)
            groupreading.save()

            reading_ids.extend([x.id for x in readers])
            print("Scheduled", groupreading.title, "on", day.day, "at", groupreading.start_time)
