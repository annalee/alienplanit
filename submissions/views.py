from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import PanelistForm
from .models import Panelist, Panel

def panel(request):
    context = {
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
                name=form['name'])
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
