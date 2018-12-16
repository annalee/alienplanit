from django.db import models

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
    day = models.CharField(
        max_length=4, blank=True,
        choices=DAY_CHOICES)
    time = models.CharField(
        max_length=10, blank=True,
        help_text="Format: <em>10AM</em>.")
    # previous will be used to make sure we're not scheduling panelists
    # for more than two panels in a row.
    previous_slot = models.OneToOneField('self', null=True,
        blank=True, on_delete=models.SET_NULL, related_name="next_slot")
    tracks = models.IntegerField(default=3,
        help_text="Number of rooms available to us in this slot.")

    def __str__(self):
        return self.day + ' ' + self.time

    class Meta:
        unique_together = ("day", "time")


class Room(models.Model):
    name = models.CharField(max_length=20, blank=True)
    av = models.BooleanField()

    def __str__(self):
        return self.name


class Experience(models.Model):
    # This model will allow us to preferentially select panelists with relevant
    # life experience, or require that experience, for some panels.
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=280, blank=True, null=True)

    def __str__(self):
        return self.name


class Panelist(models.Model):
    # this model contains some biographical info so we can avoid 'randomly'
    # creating all-white and all-male panels.
    email = models.CharField(max_length=280)
    badge_name = models.CharField(max_length=280)
    pronouns = models.CharField(max_length=280)
    a11y = models.TextField(blank=True)
    experience = models.ManyToManyField(Experience, blank=True)
    white = models.BooleanField(default=True)
    man = models.BooleanField(default=False)
    sched_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.badge_name


class Panel(models.Model):
    title = models.CharField(max_length=280)
    description = models.TextField(blank=True, null=True)
    timeslot = models.ForeignKey(Timeslot,
        blank=True, null=True, on_delete=models.SET_NULL, related_name="panels")
    av_required = models.BooleanField()
    room = models.ForeignKey(Room,
        blank=True, null=True, on_delete=models.SET_NULL)
    interested_panelists = models.ManyToManyField(
        Panelist, related_name="interested", blank=True)
    interested_moderators = models.ManyToManyField(
        Panelist, related_name="interested_mod", blank=True)
    required_panelists = models.ManyToManyField(
        Panelist, related_name="required_for", blank=True)
    final_panelists = models.ManyToManyField(
        Panelist, related_name="panels", blank=True)
    moderator = models.ForeignKey(Panelist,
        blank=True, null=True, on_delete=models.SET_NULL, related_name="moderating")
    experience = models.ManyToManyField(Experience, blank=True)
    experience_required = models.BooleanField(default=False)
    pro_track = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    def experience_check(self):
        if self.experience.exists():
            return True
        else:
            return False

    experience_check.admin_order_field = 'experience'

    def __str__(self):
        return self.title + ', ' + self.timeslot.__str__()

