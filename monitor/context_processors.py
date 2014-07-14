# -*- coding: utf-8 *-*
from django.contrib.auth.models import User
from urllib2 import quote


def common(request):
    user = request.user
    if not isinstance(user, User):
        return {}
    if not user.is_superuser:
        team = user.account.team.name
    else:
        team = ''
    is_admin = user.account.is_admin
    context = dict(
        USER_NAME=user.username,
        TEAM=team,
        TEAM_CHANNEL=quote(team.encode('utf-8')),
        app="",
        is_admin=is_admin,
        )
    return context


def static(request):
    return dict(STATIC_URL=SETTINGS.STATIC_URL)
