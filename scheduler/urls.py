from django.urls import path

from .views import index, ScheduleDisplayView, PanelistRegistrationView
from .views import PanelistRegistrationThanksView, PanelistRegistrationClosedView

urlpatterns = [
    path('', index, name='index'),
    path('<slug:conference>/',
        ScheduleDisplayView.as_view(), name='scheduledisplay'),
    path('registration/<slug:conference>/',
        PanelistRegistrationView.as_view(), name='panelistregistration'),
    path('registration/<slug:conference>/thanks/',
        PanelistRegistrationThanksView.as_view(), name='panelistregistrationthanks'),
    path('schedule/<slug:conference>/',
        ScheduleDisplayView.as_view(), name='scheduledisplay'),
]