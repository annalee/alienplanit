import factory
import random
from django.template.defaultfilters import slugify

from scheduler.models import Conference, Room, Track, Panelist, Panel


class ConferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Conference

    name = factory.Sequence(lambda n: 'TestCon {}'.format(n))

    @factory.lazy_attribute
    def slug(self):
        slug = slugify(self.name)
        return slug
    


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    conference = factory.SubFactory(ConferenceFactory)
    name = factory.Faker('city')
    capacity = 50
    category = Room.PANEL
    av = False

class TrackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Track

    name = '{} Track'.format(factory.Faker('word'))
    conference = factory.SubFactory(ConferenceFactory)

    @factory.lazy_attribute
    def slug(self):
        slug = slugify(self.name)
        return slug

class PanelistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Panelist

    email = factory.Faker('email')
    badge_name = factory.Faker('name')
    conference = factory.SubFactory(ConferenceFactory)
    inarow = 2
    reading_requested = True
    signing_requested = True

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

    title = factory.Faker('text', max_nb_chars=50)
    description = factory.Faker('paragraph', nb_sentences=6)
    conference = factory.SubFactory(ConferenceFactory)
    publish = True

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


