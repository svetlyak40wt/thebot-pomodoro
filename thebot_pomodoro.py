from __future__ import absolute_import, unicode_literals

import times
import datetime

from thebot import ThreadedPlugin, on_command


class Plugin(ThreadedPlugin):
    """An easy to use productivity management tool.

    This plugin allows you to start a timer and will
    notify when it will expire.

    Read more about pomodoro technique at:
    http://www.pomodorotechnique.com/
    """
    deps = ['notify', 'identity']

    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        self.pomodoros = self.storage.with_prefix('pomodoros:')
        self.history = self.storage.with_prefix('history:')
        self.start_worker(interval=60)

    def do_job(self):
        now = times.now()
        for key, pomodoro in self.pomodoros.items():
            if pomodoro['due'] < now:
                identity = pomodoro['identity']

                notify = self.bot.get_plugin('notify')
                notify.notify(identity, 'Pomodoro finished')

                history = self.history.get(identity.id, [])
                history.append((pomodoro['started'], (pomodoro['due'] - pomodoro['started']).seconds))
                self.history[identity.id] = history

                del self.pomodoros[key]

    @on_command('start pomodoro')
    @on_command('start pomodoro (?P<minutes>\d+)')
    def start(self, request, minutes=25):
        """Starts a timer with given interval. Default is 25 minutes."""
        identity = self.bot.get_plugin('identity').get_identity_by_request(request)

        if self.pomodoros.get(identity.id) is not None:
            request.respond('Pomodoro already started')
        else:
            now = times.now()
            self.pomodoros[identity.id] = dict(
                started=now,
                due=now + datetime.timedelta(0, int(minutes) * 60),
                identity=identity,
            )
            request.respond('Pomodoro started')

    @on_command('stop pomodoro')
    def stop(self, request):
        """Stops current timer."""
        identity = self.bot.get_plugin('identity').get_identity_by_request(request)
        pomodoro = self.pomodoros.get(identity.id)

        if pomodoro is None:
            request.respond('There is no active pomodoro')
        else:
            worked = times.now() - pomodoro['started']
            mins = worked.seconds / 60
            request.respond('Great! You\'ve worked on this pomodoro {0} minutes.'.format(mins))

            history = self.history.get(identity.id, [])
            history.append((pomodoro['started'], worked.seconds))
            self.history[identity.id] = history

            del self.pomodoros[identity.id]

    @on_command('status of pomodoro')
    def status(self, request):
        """Shows current timer's status."""
        identity = self.bot.get_plugin('identity').get_identity_by_request(request)
        pomodoro = self.pomodoros.get(identity.id)

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

    @on_command('pomodoro stats')
    def stats(self, request):
        """Shows daily stats. How many timers were started, etc.."""
        identity = self.bot.get_plugin('identity').get_identity_by_request(request)

        now = times.now()
        start_of_the_day = datetime.datetime(now.year, now.month, now.day)

        history = self.history.get(identity.id, [])
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

