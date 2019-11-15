import factory
import random
import datetime
from django.template.defaultfilters import slugify

from scheduler.models import Conference, Room, Track, Panelist, Panel, Day

class ConferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Conference

    name = factory.Sequence(lambda n: 'TestCon {}'.format(n))

    @factory.lazy_attribute
    def slug(self):
        slug = slugify(self.name)
        return slug
    
class DayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day

    conference = factory.SubFactory(ConferenceFactory)
    day = datetime.date(year=2020, month=1, day=17)
    start_time = datetime.time(hour=10)
    end_time = datetime.time(hour=19)

class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    conference = factory.SubFactory(ConferenceFactory)
    capacity = 50
    category = Room.PANEL
    av = False

    @factory.lazy_attribute
    def name(self):
        name = factory.Faker('city').generate()
        return name

class TrackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Track

    conference = factory.SubFactory(ConferenceFactory)
    start = datetime.datetime(year=2020, month=1, day=17, hour=17)
    end = datetime.datetime(year=2020, month=1, day=19, hour=16)

    @factory.lazy_attribute
    def name(self):
        name = factory.Faker('word').generate()
        return name    

    @factory.lazy_attribute
    def slug(self):
        slug = slugify(self.name)
        return slug

class PanelistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Panelist

    conference = factory.SubFactory(ConferenceFactory)
    inarow = 2
    reading_requested = True
    signing_requested = True

    @factory.lazy_attribute
    def badge_name(self):
        return factory.Faker('name').generate()

    @factory.lazy_attribute
    def email(self):
        return factory.Faker('email').generate()

    @factory.lazy_attribute
    def program_name(self):
        return self.badge_name

    @factory.lazy_attribute
    def pronouns(self):
        pronoun_choices = ['She/Her', 'He/Him', 'They/Them', 'She/They', 'E/Em']
        return random.choice(pronoun_choices)

class PanelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Panel

    description = factory.Faker('paragraph', nb_sentences=6).generate()
    conference = factory.SubFactory(ConferenceFactory)
    publish = True

    @factory.lazy_attribute
    def title(self):
        title = factory.Faker('text', max_nb_chars=50).generate()
        return title 

    @factory.post_generation
    def assign_panelists(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # select interested panelists at random
            intpan = random.randrange(3, int(len(extracted)/2))
            intmod = random.randrange(1, int(len(extracted)/4))
            for panelist in random.sample(extracted, intpan):
                self.interested_panelists.add(panelist)
            for panelist in random.sample(extracted, intmod):
                self.interested_moderators.add(panelist)

            # roll a d10 to see if this one has required panelists
            required = random.randrange(1, 10)
            # if yes, add them.
            if required == 10:
                reqmod = random.randrange(1, 4)
                for panelist in random.sample(extracted, reqmod):
                    self.required_panelist.add(panelist)

    @factory.post_generation
    def assign_track(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # assign track via a weighted random
            track = random.choices(extracted, weights=[45, 5, 5, 10, 10, 5])
            track[0].panels.add(self)


