import random
import datetime

from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from django.db.models import Q

from scheduler.models import Conference, Room, Track, Panelist, Panel

from .scheduler_factories import ConferenceFactory, RoomFactory, TrackFactory
from .scheduler_factories import PanelistFactory, PanelFactory, DayFactory

from scheduler import new_scheduler


class Test_Scheduler(TestCase):
    def setUp(self):
        self.client = Client()
        # Populate our test db
        con = ConferenceFactory(name='TestCon 2020')
        panelrooms = RoomFactory.create_batch(6, conference=con)
        readingrooms = RoomFactory.create_batch(2,
            category=Room.READING, conference=con)
        tracks = TrackFactory.create_batch(5,
                    conference=con)
        tracks.append(TrackFactory(
            start=datetime.datetime(year=2020, month=1, day=17, hour=12),
            end=datetime.datetime(year=2020, month=1, day=17, hour=18)))
        panelists = PanelistFactory.create_batch(110, conference=con)
        panels = PanelFactory.create_batch(80,
                conference=con,
                assign_panelists=panelists,
                assign_track=tracks)
        day1 = DayFactory(
                    conference=con,
                    day=datetime.date(year=2020, month=1, day=17),
                    start_time=datetime.time(hour=12),
                    end_time=datetime.time(hour=20))
        day2 = DayFactory(
                    conference=con,
                    day=datetime.date(year=2020, month=1, day=18),
                    start_time=datetime.time(hour=10),
                    end_time=datetime.time(hour=20))
        day3 = DayFactory(
                    conference=con,
                    day=datetime.date(year=2020, month=1, day=19),
                    start_time=datetime.time(hour=10),
                    end_time=datetime.time(hour=16))

    '''def test_setup(self):
        #check we've got 4 panel rooms and 2 reading rooms
        panelrooms = Room.objects.filter(category=Room.PANEL).count()
        readingrooms = Room.objects.filter(category=Room.READING).count()
        panelistcount = Panelist.objects.count()
        panelcount = Panel.objects.count()
        trackcount = Track.objects.count()

        self.assertEqual(panelrooms, 8)
        self.assertEqual(readingrooms, 2)
        self.assertEqual(panelistcount, 110)
        self.assertEqual(panelcount, 80)
        self.assertEqual(trackcount, 6)'''

    def test_schedule_integrity(self):
        # Make sure rooms are not double-booked
        con = Conference.objects.get(name='TestCon 2020')

        counter = 0
        while Panel.objects.filter(
            conference=con,
            start_time__isnull=True).count() and counter < 5:
            new_scheduler.schedule_panels(con)
            counter +=1
        print(counter)
        room = Room.objects.filter(conference=con, category=Room.READING).first()
        new_scheduler.schedule_readings(con, room)

        for room in Room.objects.filter(conference=con):
            for panel in room.panels.all():
                dupes = Panel.objects.filter(
                    room=room,
                    start_time__lte=panel.start_time,
                    end_time__gte=panel.start_time).count()
                self.assertTrue(dupes==1)  
        # and panelists aren't double-booked
        for panelist in Panelist.objects.filter(conference=con):
            for panel in panelist.panels.all():
                dupes = panelist.panels.filter(
                    start_time__lte=panel.start_time,
                    end_time__gte=panel.start_time).count()
                mdupes = panelist.moderating.filter(
                    start_time__lte=panel.start_time,
                    end_time__gte=panel.start_time)
                self.assertEqual(dupes, 1)
                self.assertEqual(mdupes.count(), 0)
            for panel in panelist.moderating.all():
                dupes = panelist.moderating.filter(
                    start_time__lte=panel.start_time,
                    end_time__gte=panel.start_time).count()
                self.assertEqual(dupes, 1)
            # and breaks are being respected
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
                self.assertTrue(recent_panel_count <= panelist.inarow)


    def test_panelist_bookings(self):
        # Make sure panelists are not double-booked
        pass

    def test_panelist_breaks(self):
        # Make sure panelists don't have more items in a row than they should
        pass



