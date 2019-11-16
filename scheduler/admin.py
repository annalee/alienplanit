from django.contrib import admin
from django.forms import ModelForm

from .models import Timeslot, Room, Experience, Panelist, Panel, Conference, Track, Day


class PanelAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PanelAdminForm, self).__init__(*args, **kwargs)
        self.fields['tracks'].queryset = Track.objects.filter(
            conference=self.instance.conference)
        self.fields['experience'].queryset = Experience.objects.filter(
            conference=self.instance.conference)
        self.fields['interested_panelists'].queryset = Panelist.objects.filter(
            conference=self.instance.conference)
        self.fields['interested_moderators'].queryset = Panelist.objects.filter(
            conference=self.instance.conference)
        self.fields['required_panelists'].queryset = Panelist.objects.filter(
            conference=self.instance.conference)
        self.fields['final_panelists'].queryset = Panelist.objects.filter(
            conference=self.instance.conference)
        self.fields['moderator'].queryset = Panelist.objects.filter(
            conference=self.instance.conference)

@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = PanelAdminForm
        return super().get_form(request, obj, **kwargs)

    list_display = ["title",
                    "moderator",
                    "start_time",
                    "room",
                    "panelists_locked",
                    "on_form"
                    ]
    list_editable = ["panelists_locked", "on_form", "publish"]
    list_filter = ("conference", ("tracks", admin.RelatedOnlyFieldListFilter))
    search_fields = ['title']
    ordering = ["title"]
    raw_id_fields = ["moderator"]
    fieldsets = (
        ("Panel Information", {
            'fields': ("title",
                       "description",
                       "notes",
                       "conference",
                       "tracks",
                       "on_form",
                       "start_time",
                       "end_time",
                       "timeslot",
                       "room",
                       "panelists_locked",
                       "publish",
                       "experience")
            }),
        ("Requirements", {
            'fields': ('av_required',
                       'roomsize',
                       'experience_required',)
            }),
        ("Panelists", {
            'fields': ("interested_panelists",
                       "interested_moderators",
                       "required_panelists",
                       "final_panelists",
                       "moderator")
            }),
        )
    filter_horizontal = ["tracks",
                         "interested_panelists",
                         "interested_moderators",
                         "required_panelists",
                         "final_panelists",
                         "experience",]


class PanelIntPanInline(admin.TabularInline):
    model = Panel.interested_panelists.through
    verbose_name = "Panels Interested In"
    verbose_name_plural = "Panels Interested In"

class PanelIntModInline(admin.TabularInline):
    model = Panel.interested_moderators.through
    verbose_name = "Volunteered to Moderate"
    verbose_name_plural = "Volunteered to Moderate"

class PanelFinalPanInline(admin.TabularInline):
    model = Panel.final_panelists.through
    verbose_name = "Panels"
    verbose_name_plural = "Final Panels"

class PanelInline(admin.TabularInline):
    model = Panel
    fields = ["title", "moderator", "final_panelists"]
    readonly_fields = ["title", "room", "timeslot", "final_panelists"]
    extra = 1
    verbose_name = "Moderating"
    verbose_name_plural = "Moderating Panels"


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "conference"]
    list_filter = ["conference"]

    class Meta:
        ordering = ["day", "time"]


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ["__str__", "day", "time", "previous_slot", "tracks"]
    list_editable = ["tracks"]
    list_display_links = ["__str__"]
    list_filter = ["conference"]
    inlines = [PanelInline,]

    class Meta:
        ordering = ["day", "time"]

class PanelistAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PanelistAdminForm, self).__init__(*args, **kwargs)
        self.fields['tracks'].queryset = Track.objects.filter(
            conference=self.instance.conference)
        self.fields['experience'].queryset = Experience.objects.filter(
            conference=self.instance.conference)

@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = PanelistAdminForm
        return super().get_form(request, obj, **kwargs)

    list_display = ["program_name", "email", "pronouns",]
    filter_horizontal = ["experience", "tracks"]
    search_fields = ['email', 'badge_name']
    inlines = [PanelIntPanInline, PanelIntModInline, PanelFinalPanInline, PanelInline]
    list_editable = []
    list_filter = ["conference", "invite_again", "pronouns", "white"]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "capacity", "category", "av", "conference"]
    list_editable = ["capacity", "category", "av", "conference"]
    list_filter = ["conference"]

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ["conference", "start_time", "end_time"]
    list_editable = ["start_time", "end_time"]
    list_filter = ["conference"]

scheduler_models = [Experience, Conference]
admin.site.register(scheduler_models)
