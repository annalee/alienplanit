from django import forms

class PanelistForm(forms.Form):
    email = forms.EmailField(label='Email address')
    name = forms.CharField(label='Name', max_length=280)
    returning = forms.BooleanField(
        label='Returning Panelist',
        help_text="Have you been a panelist at ConFusion before?",
        required=False)
    bio = forms.CharField(
        label='Bio',
        widget=forms.Textarea(attrs={'rows':3}),
        help_text="New panelist? Tell us a little about yourself. (This is for our edification only and won't be published).",
        required=False)


class PanelSubmissionForm(forms.Form):
    email = forms.EmailField(
        label='Contact Email',
        max_length=280,
        help_text="If you'd like to be on or moderate this panel, please use the same email you used on the Panelist Signup Form.")
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
