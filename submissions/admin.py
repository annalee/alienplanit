from django.contrib import admin

from .models import Panelist, Panel

@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = [
        "badge_name",
        "email",
        "conference"]
    search_fields = [
        "badge_name",
        "email"]
    readonly_fields = ["conference"]
    list_filter = ["conference"]


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "submitter_email",
        "conference"]
    search_fields = [
        "title",
        "submitter_email"]
    list_filter = ["conference"]
