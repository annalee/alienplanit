from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import PanelistForm, PanelSubmissionForm
from .models import Conference, Panelist, Panel, Textblock

from scheduler.models import Panel as SchedulerPanel
from scheduler.models import Conference as SchedulerConference
from scheduler.forms import PanelForm


@method_decorator(staff_member_required, name='dispatch')
class PendingPanelList(ListView):

    template_name = 'submissions/pendingpanellist.html'


    def get_queryset(self):
        conference = get_object_or_404(
            Conference, slug = self.kwargs['conslug'])
        return Panel.objects.filter(
            conference=conference,
            status=Panel.PENDING
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conference = get_object_or_404(
            Conference, slug = self.kwargs['conslug'])

        # Textblock for top of page
        textblock, created = Textblock.objects.get_or_create(
            slug="panelreviewlist", conference=conference)
        if created:
            textblock.title = "Pending Panel Queue"
            textblock.save()

        context['textblock'] = textblock
        context['conslug'] = conference.slug
        return context


@method_decorator(staff_member_required, name='dispatch')
class PendingPanelDetail(UpdateView):

    model = Panel
    fields = ['status']

    template_name = 'submissions/pendingpaneldetail.html'
    success_url = reverse_lazy('pending-panel-list')

    def get_panelform_initial(self):
        submission = self.object
        conid= submission.conference.slug
        notes = str(submission.notes) + '\r\n\r\n' + str(submission.staff_notes)
        initial={
                'title': submission.title,
                'description': str(submission.description),
                'roomsize': 30,
                'notes': notes,
                'tracks': [],
            }
        return initial

    def get_panelform_submitted(self):
        submission = self.request.POST
        conference = self.object.conference
        submitted={
                'title': submission['title'],
                'description': submission['description'],
                'roomsize': int(submission['roomsize']),
                'notes': submission['notes'],
                'tracks': submission.getlist('tracks'),
            }
        return submitted


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conference = self.object.conference

        # Textblock for top of page
        textblock, created = Textblock.objects.get_or_create(
            slug="panelreviewdetail", conference=conference)
        if created:
            textblock.title = "Pending Panel"
            textblock.save()

        submission = self.object
        panelform = PanelForm(
            initial=self.get_panelform_initial(),
            conslug=submission.conference.slug,
        )

        context['conslug'] = conference.slug
        context['textblock'] = textblock
        context['submitter'] = Panelist.objects.filter(
            email=submission.submitter_email).first()
        context['panel'] = submission
        context['panelform'] = panelform

        return context


    def form_invalid(self, form, **kwargs):
        context = self.get_context_data()
        context['form'] = form
        context['panelform'] = PanelForm(data=self.request.POST, conslug=self.object.conference.slug)
        return self.render_to_response(context)

    def get_success_url(self, **kwargs):
        return reverse_lazy('pending-panel-list', kwargs = {'conslug': self.object.conference.slug})

    def form_valid(self, form):
        submission = self.object
        panelform = PanelForm(conslug=submission.conference.slug, data=self.get_panelform_submitted(),
            initial=self.get_panelform_initial())
        # Panelform.has_changed() is wigging out even when
        # panelform.data == panelform.initial and I'm too tired to debug it.
        panelformhaschanged = panelform.data != panelform.initial
        print("Valid:", panelform.is_valid())
        print(panelform.errors)

        # Guardrail against folks losing data by not setting the panel status
        if panelformhaschanged and (form.instance.status != Panel.ACCEPTED):
            form.add_error('status', ValidationError(
                ("You must set the panel as accepted to save changes to editable fields."),
                code='not_accepted'))
            return self.form_invalid(form)
        # Save the submission as a SchedulerPanel if the status is accepted
        if form.instance.status == Panel.ACCEPTED:
            if panelform.is_valid():
                panelform = panelform.cleaned_data
                accepted = SchedulerPanel(
                    title = panelform['title'],
                    description = panelform['description'],
                    notes = panelform['notes'],
                    av_required = panelform['av_required'],
                    roomsize = panelform['roomsize'],
                    conference = SchedulerConference.objects.get(slug=submission.conference.slug)
                    )
                accepted.save()
                accepted.tracks.set(panelform['tracks'])
        return super().form_valid(form)


@xframe_options_exempt
@csrf_exempt
def panel(request, conslug="ConFusion2020"):

    conference = get_object_or_404(Conference, slug = conslug)

    if not conference.panel_form_open:
        # Display the "panel submissions are closed" text block.
        textblock, created = Textblock.objects.get_or_create(
            slug="panelformclosed", conference=conference)
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
                conference=conference,
                submitter_email=form['email'],
                description=form['description'],
                notes=form['notes'],
                )
            textblock, created = Textblock.objects.get_or_create(
                slug="panelthanks", conference=conference)
            if created:
                textblock.body = "Your panel idea has been submitted. We'll let you know if we're going to run it."
                textblock.save()
            context = {
                'message': textblock.body,
                'conslug': conslug
            }
            return render(request, 'submissions/thanks.html', context)
    else:
        panelform = PanelSubmissionForm()

    textblock, created = Textblock.objects.get_or_create(
        slug="panelform", conference=conference)
    if created:
        textblock.title = "Panel Submission Form"
        textblock.save()
    context = {
        'panelform': panelform,
        'title': textblock.title,
        'body': textblock.body,
        'conslug': conslug
    }
    return render(request, 'submissions/panel.html', context)


@xframe_options_exempt
@csrf_exempt
def panelist(request, conslug="ConFusion2020"):

    conference = get_object_or_404(Conference, slug = conslug)

    if not conference.panelist_form_open:
        # Display the "panelist submissions are closed" text block instead of the form.
        textblock, created = Textblock.objects.get_or_create(
            slug="panelistformclosed", conference=conference)
        if created:
            textblock.title = "The Panelist Submission Form Is Closed"
            textblock.save()
        context = {
            'title': textblock.title,
            'body': textblock.body,
        }
        return render(request, 'submissions/panelist.html', context)


    if request.method == 'POST':
        panelistform = PanelistForm(request.POST)
        if panelistform.is_valid():
            message = "We'll contact you when we're ready to register panelists."
            form = panelistform.cleaned_data
            panelist, created = Panelist.objects.get_or_create(
                email=form['email'],
                name=form['name'],
                conference=conference,
            )
            panelist.returning = form['returning']
            panelist.bio = form['bio']
            panelist.save()
            if created:
                textblock, textcreated = Textblock.objects.get_or_create(
                    slug="panelistcreated", conference=conference)
                if textcreated: 
                    textblock.body = "Thanks, your info has been recorded. " + message
                    textblock.save()
                    message = textblock.body
                else:
                    message = textblock.body

            else:
                textblock, textcreated = Textblock.objects.get_or_create(
                    slug="panelistupdated", conference=conference)
                if textcreated:
                    textblock.body = "Thanks, we've updated your info. " + message
                    textblock.save()
                    message = textblock.body
                else:
                    message = textblock.body

            context = {
                'message': message,
                'conslug': conslug
            }
            return render(request, 'submissions/thanks.html', context)
    else:
        panelistform = PanelistForm()

    textblock, created = Textblock.objects.get_or_create(
        slug="panelistform", conference=conference)
    if created:
        textblock.title = "Panelist Signup Form"
        textblock.save()

    context = {
        'panelistform': panelistform,
        'title': textblock.title,
        'body': textblock.body,
        'conslug': conslug
        }

    return render(request, 'submissions/panelist.html', context)
