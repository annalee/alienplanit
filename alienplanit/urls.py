"""alienplanit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from .settings import DEBUG
from scheduler import views

if DEBUG == True:
    admin.site.site_header = "Local Dev Admin"
    admin.site.site_title = "Local Dev Admin"
    admin.site.index_title = "Local Dev Admin"

urlpatterns = [
    path('', views.index),
    path('scheduler/', include('scheduler.urls')),
    path('submissions/', include('submissions.urls')),
    path('concom/', admin.site.urls),
]
