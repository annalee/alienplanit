from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

class Test_Pages(TestCase):
    def setUp(self):
        self.client = Client()

    def test_panel(self):
        response = self.client.get(reverse('panelist'))
        self.assertContains(response, "Panelist Signup Form")

        response = self.client.post(reverse('panel'))
        self.assertContains(response, "Panel Submission Form")

    def test_panelist(self):
        response = self.client.get(reverse('panelist'))
        self.assertContains(response, "Panelist Signup Form")

        response = self.client.post(reverse('panel'))
        self.assertContains(response, "Panel Submission Form")
