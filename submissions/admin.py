from django.contrib import admin

from .models import Panelist, Panel, Textblock

@admin.register(Panelist)
class PanelistAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "conference",
        "returning",
        "status"]
    list_editable = [
        "status"]
    search_fields = [
        "name",
        "email"]
    readonly_fields = ["conference"]
    list_filter = [
        "conference",
        "returning",
        "status"]


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "submitter_email",
        "conference"]
    search_fields = [
        "title",
        "submitter_email"]
    list_filter = [
        "conference",
        "status"]


@admin.register(Textblock)
class TextblockAdmin(admin.ModelAdmin):
    list_display = [
        "slug",
        "title",
        "body"]
    search_fields = [
        "title",
        "slug"]
    list_filter = [
        "conference"]
