from django.contrib import admin

from .models import Timeslot, Room, Experience, Panelist, Panel


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ["title", "moderator", "timeslot", "room", "experience_check", "pro_track"]
    filter_by = ["experience_check", "pro_track"]
    search_fields = ['title']
    ordering = ["title"]
    fieldsets = (
        ("Panel Information", {
            'fields': ("title",
                       "description",
                       "timeslot",
                       "room",
                       "locked",
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
                         "experience"]


class PanelIntPanInline(admin.TabularInline):
    model = Panel.interested_panelists.through

class PanelIntModInline(admin.TabularInline):
    model = Panel.interested_moderators.through

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

    class Meta:
        ordering = ["day", "time"]


@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = ["badge_name", "email", "pronouns", "sched_sent", "white"]
    filter_horizontal = ["experience",]
    search_fields = ['email', 'badge_name']
    inlines = [PanelIntPanInline, PanelIntModInline]
    list_editable = ["sched_sent"]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["name", "capacity", "category", "av"]
    list_editable = ["capacity", "category", "av"]

scheduler_models = [Experience]
admin.site.register(scheduler_models)


