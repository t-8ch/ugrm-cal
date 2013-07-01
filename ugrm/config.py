from path import path

DATADIR = str(path(__file__).dirname() / path('data') / path('usergroup'))

ADMIN_EMAIL = 'ugrm-cal@t-8ch.de'
PRODID = '-//UGRM cal//{}//'.format(ADMIN_EMAIL)
MEETING_LENGTH = 180  # in minutes
