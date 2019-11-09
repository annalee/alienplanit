from django.urls import path

from .views import index, PanelistRegistrationView, PanelistRegistrationThanksView, PanelistRegistrationClosedView

urlpatterns = [
    path('', index, name='index'),
    path('registration/<slug:conference>/', PanelistRegistrationClosedView.as_view(), name='panelistregistration'),
    path('registration/<slug:conference>/thanks/', PanelistRegistrationThanksView.as_view(), name='panelistregistrationthanks'),
]