from django.contrib import admin

from .models import Timeslot, Room, Experience, Panelist, Panel, Conference


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ["title",
                    "moderator",
                    "timeslot",
                    "room",
                    "pro_track",
                    "panelists_locked",
                    ]
    list_editable = ["panelists_locked",]
    list_filter = ["pro_track", "conference"]
    search_fields = ['title']
    ordering = ["title"]
    fieldsets = (
        ("Panel Information", {
            'fields': ("title",
                       "description",
                       "conference",
                       "timeslot",
                       "room",
                       "panelists_locked",
                       "experience")
            }),
        ("Requirements", {
            'fields': ('av_required',
                       'roomsize',
                       'experience_required',
                       'pro_track')
            }),
        ("Panelists", {
            'fields': ("interested_panelists",
                       "interested_moderators",
                       "required_panelists",
                       "final_panelists",
                       "moderator")
            }),
        )
    filter_horizontal = ["interested_panelists",
                         "interested_moderators",
                         "required_panelists",
                         "final_panelists",
                         "experience",]


class PanelIntPanInline(admin.TabularInline):
    model = Panel.interested_panelists.through

class PanelIntModInline(admin.TabularInline):
    model = Panel.interested_moderators.through

class PanelFinalPanInline(admin.TabularInline):
    model = Panel.final_panelists.through

class PanelInline(admin.TabularInline):
    model = Panel
    fields = ["title", "moderator", "final_panelists"]
    readonly_fields = ["room", "timeslot", "final_panelists"]
    extra = 1


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ["__str__", "day", "time", "previous_slot", "tracks"]
    list_editable = ["tracks"]
    list_display_links = ["__str__"]
    list_filter = ["conference"]
    inlines = [PanelInline,]

    class Meta:
        ordering = ["day", "time"]


@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = ["badge_name", "email", "pronouns", "sched_sent", "white"]
    filter_horizontal = ["experience",]
    search_fields = ['email', 'badge_name']
    inlines = [PanelFinalPanInline, PanelInline]
    list_editable = ["sched_sent"]
    readonly_fields = ["conference"]
    list_filter = ["conference"]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "capacity", "category", "av"]
    list_editable = ["capacity", "category", "av"]
    readonly_fields = ["conference"]
    list_filter = ["conference"]

scheduler_models = [Experience, Conference]
admin.site.register(scheduler_models)


