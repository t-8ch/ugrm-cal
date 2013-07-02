from path import path

DATADIR = str(path(__file__).dirname() / path('data') / path('usergroup'))

ADMIN_EMAIL = 'ugrm-cal@t-8ch.de'
PRODID = '-//UGRM cal//{}//'.format(ADMIN_EMAIL)
MEETING_LENGTH = 180  # in minutes

REMOTE_SYNC_INTERVAL = 60  # in minutes
DEFAULT_TIMEZONE = 'Europe/Berlin'
CAL_NAME = 'Usergroups RheinMain'
CAL_DESC = 'http://usergroups.rhainmainrocks.de'
