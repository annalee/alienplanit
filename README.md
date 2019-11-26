# Alien Planit
A Django app for scheduling panels for science fiction conventions.

When you've got four tracks, a hundred panels, two hundred panelists, and each panelist is on three to five panels, scheduling is hard. Alien Planit (Heh, _get it_? _Plan it_? Because it's for _planning_? :sunglasses: ) is a project to make it a little easier, by sorting your panels and panelists into a schedule where no one requires a time-turner and everyone gets reasonable breaks.

## Setup

To run the app in its current state, you will need to be comfortable with the command line interface, and you will probably also need some experience with local development environments. For now, these directions assume you are a Python/Django developer who knows your way around the command line.

1. Clone this repository.
1. set the environment variable ALIENPLANIT_SECRET_KEY.
  1. We recommend using `virtualenvwrapper` and these instructions for env variable setup: https://stackoverflow.com/a/11134336
1. Install project requirements from requirements.txt (`pip install -r requirements.txt` should do the trick).
1. From the project's root directory, run `python manage.py createsuperuser` and follow the prompts to create a user account.
1. run `python manage.py migrate` to apply migrations.
1. run `python manage.py runserver` and got to http://127.0.0.1:8000/ to see the app in action.
1. You'll need to go to http://127.0.0.1:8000/concom and log in to add panels and panelists.
1. The actual scheduling code is in `scheduler/new_scheduler.py` until we move it to a proper view.

## Use

We intend to build this app out for the con planning community, but we're not there yet.

Right now, the basic steps for planning a conference using this app are:

1. Embed the Panel and Panelist submissions forms on your conference website, and solicit submissions. Contact past speakers and let them know to sign up.

2. Accept/reject submitted panels and panelists via the admin interface and provided panel acceptance form.

3. Enter all of your panels into the app and assign tracks. You'll also want to enter information about your Days and Rooms, as explained below, but do not assign times/rooms to panels at this stage. Mark events that you wish to appear on your Panel Selection Form (to recruit panelists for them) as `on form`.

4. Contact accepted panelists and invite them to fill out the Panel Selection Form, which collects their contact details and information for the program book, in addition to collecting their panel preferences.

5. Manually schedule any events that you know need to run at certain times, such as your Opening Ceremonies. You may also choose to assign Required Panelists to some or all of your events.

6. Once you've collected panelist information and preferences, run the scheduling script. The script will choose interested panelists for each panel and assign times and rooms for each panel based on panelist availability.

7. Make any final adjustments you need.

8. Mark finalized panels with the `publish` checkbox. These panels will appear on the schedule page.



### The Submissions App
The Submissions app provides forms where interested panelists can apply to speak, and submit panels.

It further provides a form where your programming team can accept/reject panels, with accepted panels automatically saving to the **Panel** model in the Scheduler App below.

Via the admin interface, your programming team can accept/reject panelists. Panelist contact information can currently only be exported via the command line, but we intend to add features to export contact info and/or contact panelists within the app.

### The Scheduler App

The Scheduler App stores information about your conference, panels, and speakers, and provides scripts for automated panel scheduling and exporting completed schedules.

On the front end, it includes:
* A Panelist Registration/Panel Selection Form, where panelists can provide you with their details and express interest in your panels.
* A schedule display page for showing your completed schedule, with filters by day and track.

#### Models

The **Conference** model identifies a particular event you are planning (different years should have their own entries in the Conference model).

The **Day** model is where you list the days that the conference will run, with start and end times for when the app should attempt to schedule events. (Events can be manually scheduled outside these hours, but the scheduling scripts will only attempt to schedule events during the listed hours).

The **Room** model stores information about rooms into which events can be scheduled. By default, it will only automatically assign rooms of the type Panel. If using the assign_readings feature, it will assign readings to rooms of the type Reading.

**Panel** is where you put information about your actual panels.

Likewise, **Panelist** is where you put panelist info.

The **Experience** model allows you to set certain prerequisites for being on certain panels--for instance, for a panel about immigration, you might want to ask panelists if they have first-hand experience as an immigrant or refugee. Experiences can be associated with Panels and Panelists. If an experience is assigned to a panel, a checkbox where panelists can indicate they have the relevant experience with appear on the Panelist Registration/Panel Selection Form for that panel.

Information about various tracks (such as literature, fandom, media, etc) can be stored in the **Track** model, and assign tracks to panels. This affects how panels will be displayed Panelist Registration/Panel Selection Form and on the final schedule.

