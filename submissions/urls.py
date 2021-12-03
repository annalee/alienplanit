from django.urls import path

from . import views

urlpatterns = [
    path('panel/', views.panel, name='panel'),
    path('panel/<slug:conslug>/', views.panel, name='panel'),
    path('panelreview/',
        views.PendingPanelList.as_view(), name='pending-panel-list'),
    path('panelreview/<slug:conslug>/',
        views.PendingPanelList.as_view(), name='pending-panel-list'),
    path('panelreview/detail/<int:pk>/',
        views.PendingPanelDetail.as_view(), name='pending-panel-detail'),
    path('panelist/', views.panelist, name='panelist'),
    path('panelist/<slug:conslug>/', views.panelist, name='panelist'),
]