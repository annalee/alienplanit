from django import forms
from .models import Panelist, Panel, Track, Conference, Experience


class PanelForm(forms.Form):
    title = forms.CharField(
        label='Panel Title',
        max_length=280,
        help_text="Panel titles and descriptions may be edited for style, clarity, or fun.")
    description = forms.CharField(
        label='Panel Description',
        required=False,
        widget=forms.Textarea(attrs={'rows':4}),
        help_text="This should be a draft of the panel description as it would appear in the program book.")
    notes = forms.CharField(
        label='Notes for ConFusion Planners',
        widget=forms.Textarea(attrs={'rows':3}),
        required=False,
        help_text="Does this panel require a/v? Did you pre-arrange it with other panelists? Any other notes for us?"
        )
    con, created = Conference.objects.get_or_create(
        slug='ConFusion2020', name='ConFusion 2020')
    tracks = con.tracks.all()
    tracks = forms.ModelMultipleChoiceField(
        queryset = tracks,
        label='Tracks:',
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text="Select all that apply."
        )
    av_required = forms.BooleanField(
        label='AV Required',
        required=False,
        help_text="Check this box if the panel will require a projector or audio (besides mics)"
        )
    roomsize = forms.IntegerField(
        label='Room Size',
        help_text="How many audience seats should the room have?",)


class PanelistRegistrationForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=280,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': "Enter email address"})
        )
    badge_name = forms.CharField(
        label='Badge Name',
        max_length=280,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "The name that will appear on your badge"
            })
        )
    program_name = forms.CharField(
        label='Program Name',
        max_length=280,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "The name for your tent card and the program book"
            })
        )
    pronouns = forms.CharField(
        label='Pronouns',
        max_length=280,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "She/Her, They/Them, He/Him, etc"
            })
        )
    a11y = forms.CharField(
        label='Accessibility',
        required=False,
        widget=forms.Textarea(attrs={
            'rows':4,
            'class': 'form-control',
            'placeholder': "If not, please leave this field blank"
            }),
        )
    reading_requested = forms.BooleanField(
        label='reading_requested',
        required=False,
        widget= forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            })
        )
    signing_requested = forms.BooleanField(
        label='signing_requested',
        required=False,
        widget= forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            })
        )


