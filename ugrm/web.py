from flask import (Flask, abort, Response, redirect, request, render_template,
                   url_for)

from config import DATADIR
from loader import XmlLoader
from builder import build_calendar
from os import environ
from xmpp_logging_handler import XMPPHandler
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

XMPP_LOG_USER = environ.get('XMPP_LOG_USER', None)
XMPP_LOG_PASSWORD = environ.get('XMPP_LOG_PASSWORD', None)
XMPP_LOG_RECIPIENTS = environ.get('XMPP_LOG_RECIPIENTS', None)
XMPP_LOG_PORT = environ.get('XMPP_LOG_PORT', 5222)

if XMPP_LOG_USER and XMPP_LOG_PASSWORD and XMPP_LOG_RECIPIENTS:

    xmpp_handler = myHandler = XMPPHandler(XMPP_LOG_USER, XMPP_LOG_PASSWORD,
                                           XMPP_LOG_RECIPIENTS.split(','),
                                           port=XMPP_LOG_PORT)
    xmpp_handler.setLevel(logging.WARN)
    logger.addHandler(xmpp_handler)

app = Flask('ugrm')

loader = XmlLoader(DATADIR)
all_tags = list(loader.list_groups())
all_tags = sorted(all_tags)
all_groups = list(loader.load_all())
all_groups = sorted(all_groups, key=lambda x: x.tag)
all_groups_map = {}

for group in all_groups:
    all_groups_map[group.tag] = group


def build_calendar_response(groups, exclude=None):
    return Response(build_calendar(groups, exclude),
                    mimetype='text/calendar')


@app.route('/')
def index():
    return render_template('index.html', groups=all_groups,
                           calendar_url=url_for('calendar'))


@app.route('/calendar/<tag>')
def calendar_for_tag(tag):
    group = all_groups_map.get(tag, None)

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
        tags = only.split(',')

        groups = []
        for tag in tags:
            group = all_groups_map.get(tag, None)
            if group is None or group.schedule is None:
                # TODO better error reporting
                return abort(404)
            groups.append(group)

        return build_calendar_response(groups)

    exclude = request.args.get('exclude', '').split(',')

    return build_calendar_response(all_groups, exclude=exclude)
