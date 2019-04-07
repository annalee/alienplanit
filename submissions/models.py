from django.db import models

class Panelist(models.Model):
    # this collects info we can use to contact interested panelists about
    # signing up for panels
    email = models.CharField(max_length=280)
    name = models.CharField(max_length=280)
    conference = models.SlugField(max_length=50)
    returning = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Panel(models.Model):
	# this is for panel submissions
    title = models.CharField(max_length=280)
    conference = models.SlugField(max_length=50)
    submitter_email = models.CharField(max_length=280)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)