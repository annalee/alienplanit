from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from scheduler.models import Conference, Room, Track, Panelist, Panel

from .scheduler_factories import ConferenceFactory, RoomFactory, TrackFactory
from .scheduler_factories import PanelistFactory, PanelFactory

from scheduler import panel_scheduler

class Test_Scheduler(TestCase):
    def setUp(self):
        self.client = Client()
        # Populate our test db
        con = ConferenceFactory(name='TestCon 2020')
        panelrooms = RoomFactory.create_batch(4)
        readingrooms = RoomFactory.create_batch(2, category=Room.READING)

        panelists = PanelistFactory.create_batch(110, conference=con)
        panels = PanelFactory.create_batch(
            70, conference=con, assign_panelists=panelists)

        # Create the schedule
        # panel_scheduler.schedule_panels(con)

    def test_setup(self):
        #check we've got 4 panel rooms and 2 reading rooms
        panelrooms = Room.objects.filter(category=Room.PANEL).count()
        readingrooms = Room.objects.filter(category=Room.READING).count()
        panelistcount = Panelist.objects.count()
        panelcount = Panel.objects.count()

        self.assertEqual(panelrooms, 4)
        self.assertEqual(readingrooms, 2)
        self.assertEqual(panelistcount, 110)
        self.assertEqual(panelcount, 70)

    def test_room_bookings(self):
        # Make sure rooms are not double-booked
        pass

    def test_panelist_bookings(self):
        # Make sure panelists are not double-booked
        pass

    def test_panelist_breaks(self):
        # Make sure panelists don't have more items in a row than they should
        pass



