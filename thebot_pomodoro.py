from __future__ import absolute_import

import thebot
import times
import datetime


class Plugin(thebot.ThreadedPlugin):
    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.pomodoros = self.storage.with_prefix('pomodoros:')
        self.history = self.storage.with_prefix('history:')
        self.start_worker(interval=60)

    def do_job(self):
        now = times.now()
        for key, pomodoro in self.pomodoros.items():
            if pomodoro['due'] < now:
                request = pomodoro['request']
                user = unicode(request.get_user())
                request.respond('Pomodoro finished')

                history = self.history.get(user, [])
                history.append((pomodoro['started'], (pomodoro['due'] - pomodoro['started']).seconds))
                self.history[user] = history

                del self.pomodoros[key]

    @thebot.route('pomodoro start')
    @thebot.route('pomodoro start (?P<minutes>\d+)')
    def start(self, request, minutes=25):
        """Starts timer with given interval. Default is 25 minutes."""
        user = unicode(request.get_user())

        if self.pomodoros.get(user) is not None:
            request.respond('Pomodoro already started')
        else:
            now = times.now()
            self.pomodoros[user] = dict(
                started=now,
                due=now + datetime.timedelta(0, int(minutes) * 60),
                request=request,
            )
            request.respond('Pomodoro started')

    @thebot.route('pomodoro stop')
    def stop(self, request):
        user = unicode(request.get_user())
        pomodoro = self.pomodoros.get(user)

        if pomodoro is None:
            request.respond('There is no active pomodoro')
        else:
            worked = times.now() - pomodoro['started']
            mins = worked.seconds / 60
            request.respond('Great! You\'ve worked on this pomodoro {0} minutes.'.format(mins))

            history = self.history.get(user, [])
            history.append((pomodoro['started'], worked.seconds))
            self.history[user] = history

            del self.pomodoros[user]

    @thebot.route('pomodoro status')
    def status(self, request):
        user = unicode(request.get_user())
        pomodoro = self.pomodoros.get(user)

        if pomodoro is None:
            request.respond('There is no active pomodoro')
        else:
            now = times.now()
            worked = pomodoro['due'] - now
            mins = max(0, worked.seconds / 60)
            secs = max(0, worked.seconds % 60)

            if worked.days < 0:
                request.respond('You pomodoro almost finished.')
            else:
                if mins > 0:
                    request.respond('{0} minutes till the end of the current pomodoro.'.format(mins))
                else:
                    request.respond('{0} seconds till the end of the current pomodoro.'.format(secs))

    @thebot.route('pomodoro stats')
    def stats(self, request):
        user = unicode(request.get_user())
        now = times.now()
        start_of_the_day = datetime.datetime(now.year, now.month, now.day)

        history = self.history.get(user, [])
        history = [
            (started, duration)
            for started, duration in history
                if started > start_of_the_day
        ]
        if history:
            request.respond(
                'There were {} pomodoros with cumulative length of {} minutes.'.format(
                    len(history),
                    sum(h[1] for h in history) / 60,
                )
            )
        else:
            request.respond('There is no finished pomodoros today.')

