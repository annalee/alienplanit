from django import forms

class PanelistForm(forms.Form):
    email = forms.CharField(label='Email address', max_length=280)
    name = forms.CharField(label='Name', max_length=280)
    returning = forms.BooleanField(label='I have been a panelist at ConFusion before')
