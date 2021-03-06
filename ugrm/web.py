from flask import (Flask, abort, Response, redirect, request, render_template,
                   url_for, send_from_directory)
from raven.contrib.flask import Sentry

from config import DATADIR, SENTRY_DSN, UGRM_URL
from loader import LocalDirectoryLoader
from builder import build_calendar
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask('ugrm')
if SENTRY_DSN:
    sentry = Sentry(app, dsn=SENTRY_DSN)

loader = LocalDirectoryLoader(DATADIR)
all_slugs = list(loader.list_groups())
all_slugs = sorted(all_slugs)
all_groups = list(loader.load_all())
all_groups = sorted(all_groups, key=lambda x: x.slug)
all_groups_map = {}

for group in all_groups:
    all_groups_map[group.slug] = group


def build_calendar_response(groups, exclude=None):
    return Response(build_calendar(groups, exclude),
                    mimetype='text/calendar')


@app.route('/')
def index():
    return render_template('index.html', groups=all_groups,
                           ugrm_url=UGRM_URL,
                           calendar_url=url_for('calendar'))


@app.route('/calendar/<slug>')
def calendar_for_slug(slug):
    group = all_groups_map.get(slug, None)

    if group is None or group.schedule is None:
        return abort(404)

    alternative_url = group.schedule.alternative_url()
    if alternative_url is not None:
        return redirect(alternative_url)

    return build_calendar_response([group])


@app.route('/calendar')
def calendar():
    only = request.args.get('only', None)
    if only is not None:
        slugs = only.split(',')

        groups = []
        for slug in slugs:
            group = all_groups_map.get(slug, None)
            if group is None or group.schedule is None:
                # TODO better error reporting
                return abort(404)
            groups.append(group)

        return build_calendar_response(groups)

    exclude = request.args.get('exclude', '').split(',')

    return build_calendar_response(all_groups, exclude=exclude)


@app.route('/calendar/tag')
def calendar_by_tag():
    only = request.args.get('only', None)
    if only is not None:
        tags = set(only.split(','))
        selected_groups = []

        for group in all_groups:
            for group_tag in group.tags:
                if group_tag.lower() in tags:
                    selected_groups.append(group)

        return build_calendar_response(selected_groups)

    return build_calendar_response(all_groups)


@app.route('/thumbnail/<thumbnail>')
def thumbnail(thumbnail):
    parts = thumbnail.split('.')
    if not parts or parts[-1] not in ['png', 'jpg']:
        abort(404)
    return send_from_directory(DATADIR, thumbnail)
