# -*- coding: utf-8 *-*

from tgdemand import CONTEXT_PATH
from tgdemand import UPLOAD_PATH
from tgdemand import SETTINGS


def common(request):
    user = request.user

    context = dict(
        UPLOAD_PATH=UPLOAD_PATH,
        CONTEXT_PATH=CONTEXT_PATH,
        app=""
        )
    return context


def static(request):
    return dict(STATIC_URL=SETTINGS.STATIC_URL)
