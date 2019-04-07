from django.shortcuts import render
from django.http import HttpResponse

def panel(request):
    context = {
        'declaration': "I am a panel submission!"
        }
    return render(request, 'submissions/panel.html', context)


def panelist(request):
    context = {
        'declaration': "I am a panelist submission!"
        }
    return render(request, 'submissions/panelist.html', context)
