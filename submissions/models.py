from django.db import models

class Conference(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=280)
    panelist_form_open = models.BooleanField(default=False)
    panel_form_open = models.BooleanField(default=False)

    def __str__(self):
        return self.slug


class Panelist(models.Model):
    # this collects info we can use to contact interested panelists about
    # signing up for panels
    INVITE = "yes"
    NOINVITE = "no"
    PENDING = "pen"
    WITHDREW = "w"
    STATUS_CHOICES = [
        (INVITE, 'Invited'),
        (NOINVITE, 'Not Invited'),
        (PENDING, 'Pending'),
        (WITHDREW, 'Withdrew')
    ]

    email = models.CharField(max_length=280)
    name = models.CharField(max_length=280)
    conference = models.ForeignKey(
        Conference,
        on_delete = models.CASCADE,
        related_name = 'Panelists',
        default= 1
   )
    returning = models.BooleanField(default=False)
    bio = models.TextField(
        blank=True,
        null=True,)
    staff_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for conference staff about the panelist.")
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return self.name


class Panel(models.Model):
    # this is for panel submissions

    ACCEPTED = "yes"
    REJECTED = "no"
    PENDING = "pen"
    STATUS_CHOICES = [
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
    ]

    title = models.CharField(max_length=280)
    conference = models.ForeignKey(
        Conference,
        on_delete = models.CASCADE,
        related_name = 'Panels',
        default= 1
   )
    submitter_email = models.CharField(max_length=280)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    staff_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes for conference staff about the submission.")
    status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def get_absolute_url(self):
        return reverse('pending-panel-detail', kwargs={'pk': self.pk})


class Textblock(models.Model):
    slug=models.SlugField(max_length=50)
    conference = models.ForeignKey(
        Conference,
        on_delete = models.CASCADE,
        related_name = 'Textblocks',
        default= 1
   )
    title=models.CharField(max_length=280, blank=True, null=True)
    body=models.TextField(blank=True, null=True)

    models.UniqueConstraint(
        fields=['slug', 'conference'], name='unique_textblock')
