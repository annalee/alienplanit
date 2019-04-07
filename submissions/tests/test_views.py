from django.test import Client, SimpleTestCase
from django.urls import reverse

class Test_Pages(SimpleTestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_panel(self):
        response = self.client.get(reverse('panel'))

        self.assertContains(response, "I am a panel submission!")

    def test_panelist(self):
        response = self.client.get(reverse('panelist'))

        self.assertContains(response, "I am a panelist submission!")
