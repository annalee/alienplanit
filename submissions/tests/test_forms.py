from django.test import Client, SimpleTestCase

from submissions.forms import PanelSubmissionForm, PanelistForm


class Test_Forms(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_panel_submission_form(self):
        form_data = {
            'email': 'leia.organa@resistance.org',
            'title': "The Force And Why It's With Us",
            'description': 'Descriptions are required',
            'notes': ''
            }
        form = PanelSubmissionForm(data=form_data)
        self.assertTrue(form.is_valid())


    def test_panelist_submission_form(self):
        form_data = {
            'email': 'poe.dameron@resistance.org',
            'name': "Poe Dameron",
            'Returning': '',
            }
        form = PanelistForm(data=form_data)
        self.assertTrue(form.is_valid())
