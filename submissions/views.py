from django.shortcuts import render
from django.http import HttpResponse

def panel(request):
    return HttpResponse("I'm a panel submission!")


def panelist(request):
    return HttpResponse("I'm a panelist submission!")