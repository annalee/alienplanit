from django.db import models
from django.db.models import F, Q

from django.db.models.constraints import CheckConstraint


class Conference(models.Model):
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=280)
    panelist_registration_open = models.BooleanField()

    def __str__(self):
        return self.slug


class Day(models.Model):
    conference = models.ForeignKey(Conference, related_name='days', on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.conference.slug + str(self.day)

class Timeslot(models.Model):
    # We're not using datetime for this because the system doesn't actually need
    # to know these are dates and times, and I don't hate myself.
    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'
    DAY_CHOICES = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    )
    conference = models.ForeignKey(Conference,
        null=True, on_delete=models.SET_NULL, related_name="timeslots")
    day = models.CharField(max_length=4, blank=True, choices=DAY_CHOICES)
    time = models.CharField(max_length=10, blank=True,
                            help_text="Format: <em>10AM</em>.")
    # previous will be used to make sure we're not scheduling panelists
    # for too many panels in a row.
    previous_slot = models.OneToOneField('self', null=True,
        blank=True, on_delete=models.SET_NULL, related_name="next_slot")
    tracks = models.IntegerField(default=3,
        help_text="Number of rooms available to us in this slot.")
    reading_slots = models.IntegerField(default=3,
        help_text="Number of readings available this slot.")

    def __str__(self):
        return self.day + ' ' + self.time

    class Meta:
        unique_together = ("day", "time", "conference")


class Room(models.Model):
    PANEL = 'panel'
    READING = 'reading'
    SPECIAL = 'special'
    CATEGORY_CHOICES = (
        (PANEL, 'panel'),
        (READING, 'reading'),
        (SPECIAL, 'special'),
    )
    conference = models.ForeignKey(Conference,
        null=True, on_delete=models.SET_NULL, related_name="rooms")
    name = models.CharField(max_length=20, blank=True)
    capacity = models.IntegerField(help_text="Audience capacity.")
    category = models.CharField(
        max_length=10, blank=True, choices=CATEGORY_CHOICES)
    av = models.BooleanField()

    def __str__(self):
        return str(self.conference) + ': ' + self.name


class Experience(models.Model):
    # This model will allow us to preferentially select panelists with relevant
    # life experience, or require that experience, for some panels.
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=280, blank=True, null=True)
    conference = models.ForeignKey(Conference,
        null=True, on_delete=models.SET_NULL, related_name="experiences")

    def __str__(self):
        return self.name

class Track(models.Model):
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=280)
    conference = models.ForeignKey(Conference,
        null=True, on_delete=models.SET_NULL, related_name="tracks")
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    schedule = models.BooleanField(default=True)
    limit_concurrent = models.IntegerField(
        help_text="Limit how many panels can run at once (zero for no limit)",
        default=0)

    def __str__(self):
        return "[" + self.conference.slug+"] " + self.name

    class Meta:
        unique_together = ("slug", "conference")


class Panelist(models.Model):
    # this model contains some biographical info so we can avoid 'randomly'
    # creating all-white and all-male panels.
    email = models.CharField(max_length=280)
    badge_name = models.CharField(max_length=280)
    program_name = models.CharField(max_length=280)
    conference = models.ForeignKey(Conference,
        null=True, blank=True, on_delete=models.SET_NULL, related_name="panelists")
    tracks = models.ManyToManyField(Track,
        blank=True, related_name="panelists")
    available_from = models.DateTimeField(blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    pronouns = models.CharField(max_length=280)
    a11y = models.TextField(blank=True)
    inarow = models.IntegerField(default=2,
        help_text="Number of panels this person can do in a row.")
    experience = models.ManyToManyField(Experience, blank=True)
    white = models.BooleanField(default=True)
    man = models.BooleanField(default=False)
    sched_sent = models.BooleanField(default=False)
    reading_requested = models.BooleanField(default=False)
    signing_requested = models.BooleanField(default=False)
    invite_again = models.BooleanField(default=True)
    staff_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.program_name


class Panel(models.Model):
    title = models.CharField(max_length=280)
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True,
        help_text="Internal notes for conference planners.")
    conference = models.ForeignKey(Conference,
        null=True, on_delete=models.SET_NULL, related_name="panels")
    tracks = models.ManyToManyField(Track,
        blank=True, related_name="panels")
    on_form = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    timeslot = models.ForeignKey(Timeslot,
        blank=True, null=True, on_delete=models.SET_NULL, related_name="panels")
    av_required = models.BooleanField(default=False)
    roomsize = models.IntegerField(
        help_text="How many audience seats should the room have?",
        default=30)
    room = models.ForeignKey(Room,
        blank=True, null=True, on_delete=models.SET_NULL, related_name="panels")
    interested_panelists = models.ManyToManyField(
        Panelist, related_name="interested", blank=True)
    interested_moderators = models.ManyToManyField(
        Panelist, related_name="interested_mod", blank=True)
    required_panelists = models.ManyToManyField(
        Panelist, related_name="required_for", blank=True)
    final_panelists = models.ManyToManyField(
        Panelist, related_name="panels", blank=True)
    moderator = models.ForeignKey(Panelist, blank=True, null=True,
        on_delete=models.SET_NULL, related_name="moderating")
    experience = models.ManyToManyField(Experience, blank=True)
    experience_required = models.BooleanField(default=False)
    panelists_locked = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)


    def experience_check(self):
        if self.experience.exists():
            return True
        else:
            return False

    experience_check.admin_order_field = 'experience'

    def __str__(self):
        if self.start_time:
            return self.title + ', ' + self.start_time.strftime("%a %-I:%M%p")
        else:
            return self.title
    class Meta:
        unique_together = ("room", "timeslot", "conference")
        constraints = [
            CheckConstraint(
                check=Q(start_time__lte=F('end_time')),
                name="valid-time")
        ]