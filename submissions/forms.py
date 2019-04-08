from django import forms

class PanelistForm(forms.Form):
    email = forms.EmailField(label='Email address')
    name = forms.CharField(label='Name', max_length=280)
    returning = forms.BooleanField(
        label='Returning Panelist',
        help_text="Have you been a panelist at ConFusion before?",
        required=False)


class PanelSubmissionForm(forms.Form):
    email = forms.EmailField(label='Contact Email', max_length=280)
    title = forms.CharField(label='Panel Title', max_length=280)
    description = forms.CharField(label='Panel Description', widget=forms.Textarea)
    notes = forms.CharField(
        label='Notes for ConFusion Planners',
        widget=forms.Textarea,
        required=False,
        help_text="Do you have specific panelists in mind? Require a/v? Any other notes for us?"
        )
