# -*- coding: utf-8 *-*
from django.contrib.auth.models import User
from urllib2 import quote


def common(request):
    user = request.user
    if not isinstance(user, User):
        return {}
    if not user.is_superuser:
        team = user.account.team.name
        team_id = user.account.team.id
    else:
        team = ''
        team_id = ''
    is_admin = user.account.is_admin
    context = dict(
        USER_NAME=user.username,
        TEAM=team,
        TEAM_CHANNEL=team_id,
        app="",
        is_admin=is_admin,
        )
    return context


def static(request):
    return dict(STATIC_URL=SETTINGS.STATIC_URL)
