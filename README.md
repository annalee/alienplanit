# Alien Planit
A Django app for scheduling panels for science fiction conventions.

When you've got four tracks, a hundred panels, two hundred panelists, and each panelist is on three to five panels, scheduling is hard. Alien Planit (Heh, _get it_? _Plan it_? Because it's for _planning_? :sunglasses: ) is a project to make it a little easier, by sorting your panels and panelists into a schedule where no one requires a time-turner and everyone gets reasonable breaks.

## Setup

To run the app in its current state, you will need to be comfortable with the command line interface, and you will probably also need some experience with local development environments. For now, these directions assume you are a Python/Django developer who knows your way around the command line.

1. Clone this repository.
1. set the environment variable ALIENPLANIT_SECRET_KEY.
  1. We recommend using `virtualenvwrapper` and these instructions for env variable setup: https://stackoverflow.com/a/11134336
1. From the project's root directory, run `python manage.py createsuperuser` and follow the prompts to create a user account.
1. run `python manage.py migrate` to apply migrations.
1. run `python manage.py runserver` and got to http://127.0.0.1:8000/ to see the app in action.
1. You'll need to go to http://127.0.0.1:8000/admin and log in to add panels and panelists.
1. The actual scheduling code is in `scheduler/panel_scheduler.py` until we move it to a proper view.

## Use

We intend to build this app out for the con planning community, but we're not there yet. We'll update this readme when we're ready for users.

The *Timeslots* model allows you to supply slots you'd like to fill with panels. We're not currently using datetime for this, because the system doesn't need to know these are times--it thinks of them as _slots_ to fill. For every slot other than the first slot of the day, specify a *previous slot* so that the app can tell which panelists have already done two panels in a row and need a break. *Tracks* indicates the number of panels that can be concurrently scheduled in that slot.

The *Rooms* model is under-used at the moment, but is designed to be used when you need to assign specific panels to specific rooms--because you need that panel in your largest space, or in one of the rooms with A/V equipment, etc.

*Panels* is where you put information about your actual panels.

Likewise, *Panelists* is where you put panelist info.

The *Experiences* model allows you to set certain prerequisites for being on certain panels--for instance, for a panel about immigration, you might want to ask panelists if they have first-hand experience as an immigrant or refugee. You then attach that experience to the panel it's required for, and you add it to the relevant panelist's profiles so that the scheduler can preferentially (or, if `experience_required` is checked for the panel, exclusively) schedule panelists with the relevant experience (this isn't implemented in the scheduler yet).

