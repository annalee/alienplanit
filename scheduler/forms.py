from django import forms
from .models import Panelist, Panel, Track, Conference


class PanelForm(forms.Form):
    title = forms.CharField(
        label='Panel Title',
        max_length=280,
        help_text="Panel titles and descriptions may be edited for style, clarity, or fun.")
    description = forms.CharField(
        label='Panel Description',
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


