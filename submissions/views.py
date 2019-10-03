from django import forms
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy

from .forms import PanelistForm, PanelSubmissionForm
from .models import Panelist, Panel, Textblock

from scheduler.models import Panel as SchedulerPanel
from scheduler.models import Conference as SchedulerConference
from scheduler.forms import PanelForm

@method_decorator(staff_member_required, name='dispatch')
class PendingPanelList(ListView):

    template_name = 'submissions/pendingpanellist.html'

    def get_queryset(self):
        return Panel.objects.filter(status=Panel.PENDING)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Textblock for top of page
        textblock, created = Textblock.objects.get_or_create(
            slug="panelreviewlist", conference="ConFusion2020")
        if created:
            textblock.title = "Pending Panel Queue"
            textblock.save()

        context['textblock'] = textblock
        return context

@method_decorator(staff_member_required, name='dispatch')
class PendingPanelDetail(UpdateView):

    model = Panel
    fields = ['status']

    template_name = 'submissions/pendingpaneldetail.html'
    success_url = reverse_lazy('pending-panel-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Textblock for top of page
        textblock, created = Textblock.objects.get_or_create(
            slug="panelreviewdetail", conference="ConFusion2020")
        if created:
            textblock.title = "Pending Panel"
            textblock.save()

        submission = self.object
        notes = submission.notes + '\n\n' + submission.staff_notes

        context['textblock'] = textblock
        context['submitter'] = Panelist.objects.filter(email=submission.submitter_email).first()
        context['panel'] = submission
        context['panelform'] = PanelForm(
            initial={
                'title': submission.title,
                'description': submission.description,
                'roomsize': 30,
                'notes': notes
            }
        )

        return context

    def form_valid(self, form):
        # Save the submission as a SchedulerPanel if the status is accepted
        if form.instance.status == Panel.ACCEPTED:
            panelform = PanelForm(self.request.POST)
            if panelform.is_valid():
                panelform = panelform.cleaned_data 
                accepted = SchedulerPanel(
                    title = panelform['title'],
                    description = panelform['description'],
                    conference = SchedulerConference.objects.filter(
                        slug=form.instance.conference).first(),
                    notes = panelform['notes'],
                    av_required = panelform['av_required'],
                    roomsize = panelform['roomsize'],
                    )
                accepted.save()
                accepted.tracks.set(panelform['tracks'])
        return super().form_valid(form)


@xframe_options_exempt
@csrf_exempt
def panel(request):

    # Panel submissions are closed. TODO: move this into an admin setting
    textblock, created = Textblock.objects.get_or_create(slug="panelformclosed", conference="ConFusion2020")
    if created:
        textblock.title = "The Panel Submission Form Is Closed"
        textblock.save()
    context = {
        'title': textblock.title,
        'body': textblock.body,
    }
    return render(request, 'submissions/panel.html', context)

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


@xframe_options_exempt
@csrf_exempt
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
            panelist.bio = form['bio']
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
