from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import PanelistForm, PanelSubmissionForm
from .models import Panelist, Panel

def panel(request):
    if request.method == 'POST':
        panelform = PanelSubmissionForm(request.POST)
        if panelform.is_valid():
            form = panelform.cleaned_data
            panel, created = Panel.objects.get_or_create(
                title=form['title'],
                conference="TestFusion2020",
                submitter_email=form['email'],
                description=form['description'],
                notes=form['notes'],
                )
            # TODO turn the into an actual page.
            return HttpResponse("Thanks, your panel has been submitted.")
    else:
        panelform = PanelSubmissionForm()

    context = {
        'panelform': panelform,
        'declaration': "I am a panel submission!"
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
                conference="TestFusion2020")
            # TODO turn the into an actual page.
            if created:
                return HttpResponse("Thanks, your info has been recorded.")
            else:
                return HttpResponse("Thanks, your info has been updated.")
    else:
        panelistform = PanelistForm()

    context = {
        'panelistform': panelistform,
        'declaration': "I am a panelist submission!"
        }
    return render(request, 'submissions/panelist.html', context)
