from django.contrib import admin

from .models import Timeslot, Room, Experience, Panelist, Panel


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ["title", "timeslot", "room", "experience_check", "pro_track"]
    filter_by = ["experience_check"]
    search_fields = ['title']
    ordering = ["title"]
    fieldsets = (
        ("Panel Information", {
            'fields': ("title", "timeslot", "room", "experience")
            }),
        ("Requirements", {
            'fields': ('av_required', 'experience_required', 'pro_track')
            }),
        ("Panelists", {
            'fields': ("interested_panelists",
                       "required_panelists",
                       "final_panelists")
            }),
        )
    filter_horizontal = ["interested_panelists",
                         "required_panelists",
                         "final_panelists",
                         "experience"]


class Panel1Inline(admin.TabularInline):
    model = Panel.final_panelists.through

class PanelInline(admin.TabularInline):
    model = Panel
    fields = ["title", "final_panelists"]
    filter_horizontal = ["final_panelists"]
    extra = 1


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ["__str__", "day", "time", "previous_slot", "tracks"]
    list_editable = ["day", "time", "previous_slot", "tracks"]
    list_display_links = ["__str__"]
    inlines = [PanelInline,]


@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = ["badge_name", "pronouns", "sched_sent", "person_of_color"]
    filter_horizontal = ["experience",]
    search_fields = ['badge_name']
    inlines = [Panel1Inline,]
    list_editable = ["sched_sent"]

scheduler_models = [Room, Experience]
admin.site.register(scheduler_models)


