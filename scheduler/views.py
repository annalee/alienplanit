from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy

from .models import Conference, Experience, Panelist, Panel, Track
from .forms import PanelistRegistrationForm


def index(request):
    return HttpResponse(
        '"Time, like water, expands when frozen." -Amal El-Mohtar')

class PanelistRegistrationView(FormView):


    form_class = PanelistRegistrationForm
    template_name = "scheduler/registration.html"

    def get_success_url(self, **kwargs):
        return reverse_lazy('panelistregistrationthanks',
        kwargs={'conference': self.kwargs['conference']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the conference from the url
        conference = get_object_or_404(
            Conference, slug=self.kwargs['conference'])

        # Get the approved panels by track
        conference_panels = Panel.objects.filter(
                conference=conference,
                on_form=True).prefetch_related(
                'experience')
        tracks = Track.objects.filter(conference=conference)

        panels = {}
        displaytracks = []
        for track in tracks:
            trackpanels = conference_panels.filter(
                tracks=track).order_by('title')
            if trackpanels:
                panels[track] = trackpanels
                displaytracks.append(track.slug)

        context['panels'] = panels
        context['trackslugs'] = displaytracks
        context['conference'] = conference
        return context


    def form_invalid(self, form, **kwargs):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        submission = self.request.POST
        con = self.get_context_data()['conference']
        data = form.cleaned_data
        panelist_ids = submission.getlist('panel_panelist')
        moderator_ids = submission.getlist('panel_moderator')
        xp_ids = submission.getlist('panel_xp')

        # The panel, moderator, and xp info isn't validated by the form because
        # we're handling those form elements manually. It's unlikely anyone will
        # bother to submit junk POST data, but we'll clean it to be safe.
        valid_panel_ids = [x.id for x in Panel.objects.filter(
            conference=con, on_form=True)]
        valid_xp_ids = [x.id for x in Experience.objects.filter(
            conference=con)]

        panelist_ids = [x for x in panelist_ids if int(x) in valid_panel_ids]
        moderator_ids = [x for x in moderator_ids if int(x) in valid_panel_ids]
        xp_ids = [x for x in xp_ids if int(x) in valid_xp_ids]

        white = True
        if ('panelistPersonOfColor' in submission.keys() and 
            submission['panelistPersonOfColor'] in ["yes", "comp"]):
            white = False

        man = False
        male_pronouns = ["He/Him", "he/him", "he"]
        male_gender = ["Man", "man", "Male", "male"]
        if (data['pronouns'] in male_pronouns or
            submission['gender'] in male_gender):
            man = True

        notes = "gender: " + submission['gender'] + " race: " + submission['race']

        panelist = Panelist(
            email = data['email'],
            badge_name = data['badge_name'],
            program_name = data['program_name'],
            conference = con,
            pronouns = data['pronouns'],
            a11y = data['a11y'],
            white = white,
            man = man,
            reading_requested = data['reading_requested'],
            signing_requested = data['signing_requested'],
            staff_notes = notes
            )
        panelist.save()

        panelist.interested.add(*panelist_ids)
        panelist.interested_mod.add(*moderator_ids)
        panelist.experience.add(*xp_ids)

        if 'pro-track-avail' in submission.keys():
            panelist.tracks.add(Track.objects.get(conference=con, slug='pro'))

        return super().form_valid(form)


class PanelistRegistrationThanksView(TemplateView):

    template_name = "scheduler/registration-thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conference = get_object_or_404(
            Conference, slug=kwargs['conference'])

        context['conference'] = conference
        return context

class PanelistRegistrationClosedView(TemplateView):

    template_name = "scheduler/registration-closed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conference = get_object_or_404(
            Conference, slug=kwargs['conference'])

        context['conference'] = conference
        return context
