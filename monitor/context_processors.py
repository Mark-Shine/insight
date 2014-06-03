# -*- coding: utf-8 *-*
from django.contrib.auth.models import User


def common(request):
    user = request.user
    if not isinstance(user, User):
        return {}
    if not user.is_superuser:
        team = user.account.team.name
    else:
        team = ''
    context = dict(
        USER_NAME=user.username,
        TEAM=team,
        app=""
        )
    return context


def static(request):
    return dict(STATIC_URL=SETTINGS.STATIC_URL)
