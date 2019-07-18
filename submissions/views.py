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
            textblock, created = Textblock.objects.get_or_create(slug="panelthanks", conference="ConFusion2020")
            if created:
                textblock.body = "Your panel idea has been submitted. We'll let you know if we're going to run it."
                textblock.save()
            context = {
                'message': textblock.body,
            }
            return render(request, 'submissions/thanks.html', context)
    else:
        panelform = PanelSubmissionForm()

    textblock, created = Textblock.objects.get_or_create(slug="panelform", conference="ConFusion2020")
    if created:
        textblock.title = "Panel Submission Form"
        textblock.save()
    context = {
        'panelform': panelform,
        'title': textblock.title,
        'body': textblock.body,
    }
    return render(request, 'submissions/panel.html', context)


def panelist(request):
    if request.method == 'POST':
        panelistform = PanelistForm(request.POST)
        if panelistform.is_valid():
            message = "We'll contact you when we're ready to register panelists."
            form = panelistform.cleaned_data
            panelist, created = Panelist.objects.get_or_create(
                email=form['email'],
                name=form['name'],
                conference="ConFusion2020",
            )
            panelist.returning = form['returning']
            panelist.save()
            if created:
                textblock, textcreated = Textblock.objects.get_or_create(slug="panelistcreated", conference="ConFusion2020")
                if textcreated: 
                    textblock.body = "Thanks, your info has been recorded. " + message
                    textblock.save()
                    message = textblock.body
                else:
                    message = textblock.body

            else:
                textblock, textcreated = Textblock.objects.get_or_create(slug="panelistupdated", conference="ConFusion2020")
                if textcreated:
                    textblock.body = "Thanks, we've updated your info. " + message
                    textblock.save()
                    message = textblock.body
                else:
                    message = textblock.body

            context = {
                'message': message,
            }
            return render(request, 'submissions/thanks.html', context)
    else:
        panelistform = PanelistForm()

    textblock, created = Textblock.objects.get_or_create(slug="panelistform", conference="ConFusion2020")
    if created:
        textblock.title = "Panelist Signup Form",
        textblock.save()

    context = {
        'panelistform': panelistform,
        'title': textblock.title,
        'body': textblock.body
        }

    return render(request, 'submissions/panelist.html', context)
