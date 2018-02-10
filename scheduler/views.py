from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('"Time, like water, expands when frozen." -Amal El-Mohtar')
