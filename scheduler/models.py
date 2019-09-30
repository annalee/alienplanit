from django.db import models

class Conference(models.Model):
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=280)

    def __str__(self):
        return self.slug

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

    def __str__(self):
        return self.conference.name + self.name

    class Meta:
        unique_together = ("slug", "conference")


class Panelist(models.Model):
    # this model contains some biographical info so we can avoid 'randomly'
    # creating all-white and all-male panels.
    email = models.CharField(max_length=280)
    badge_name = models.CharField(max_length=280)
    conference = models.ForeignKey(Conference,
        null=True, blank=True, on_delete=models.SET_NULL, related_name="panelists")
    tracks = models.ManyToManyField(Track,
        blank=True, related_name="panelists")
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
        return self.badge_name


class Panel(models.Model):
    title = models.CharField(max_length=280)
    description = models.TextField(blank=True, null=True)
    conference = models.ForeignKey(Conference,
        null=True, on_delete=models.SET_NULL, related_name="panels")
    tracks = models.ManyToManyField(Track,
        blank=True, related_name="panels")
    timeslot = models.ForeignKey(Timeslot,
        blank=True, null=True, on_delete=models.SET_NULL, related_name="panels")
    av_required = models.BooleanField(default=False)
    roomsize = models.IntegerField(
        help_text="How many audience seats should the room have?")
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


    def experience_check(self):
        if self.experience.exists():
            return True
        else:
            return False

    experience_check.admin_order_field = 'experience'

    def __str__(self):
        return self.title + ', ' + self.timeslot.__str__()

    class Meta:
        unique_together = ("room", "timeslot", "conference")

