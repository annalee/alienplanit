from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import PanelistForm, PanelSubmissionForm
from .models import Panelist, Panel, Textblock

def panel(request):
    if request.method == 'POST':
        panelform = PanelSubmissionForm(request.POST)
        if panelform.is_valid():
            form = panelform.cleaned_data
            panel, created = Panel.objects.get_or_create(
                title=form['title'],
                conference="ConFusion2020",
                submitter_email=form['email'],
                description=form['description'],
                notes=form['notes'],
                )
            # TODO turn the into an actual page.
            return HttpResponse("Thanks, your panel has been submitted.")
    else:
        panelform = PanelSubmissionForm()

    try:
        textblock = Textblock.objects.get(slug="panelform", conference="ConFusion2020")
        context = {
        'panelform': panelform,
        'title': textblock.title,
        'body': textblock.body
        }
    except Textblock.DoesNotExist as e:
        context = {
            'panelform': panelform,
            'title': "Panel Submission Form",
            'body': ''
            }
    return render(request, 'submissions/panel.html', context)


def panelist(request):
    if request.method == 'POST':
        panelistform = PanelistForm(request.POST)
        if panelistform.is_valid():
            form = panelistform.cleaned_data
            panelist, created = Panelist.objects.get_or_create(
                email=form['email'],
                name=form['name'],
                conference="ConFusion2020")
            # TODO turn the into an actual page.
            if created:
                return HttpResponse("Thanks, your info has been recorded. We'll contact you when we're ready to register panelists.")
            else:
                return HttpResponse("Thanks, your info has been updated. We'll contact you when we're ready to register panelists.")
    else:
        panelistform = PanelistForm()

    try:
        textblock = Textblock.objects.get(slug="panelistform", conference="ConFusion2020")
        context = {
            'panelistform': panelistform,
            'title': textblock.title,
            'body': textblock.body
            }
    except Textblock.DoesNotExist as e:
        context = {
            'panelistform': panelistform,
            'title': "Panelist Signup Form",
            'body': ''
        }
    return render(request, 'submissions/panelist.html', context)
