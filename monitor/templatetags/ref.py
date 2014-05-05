# -*- coding: utf-8 *-*
from os import path
from django import template
register = template.Library()


@register.tag(name='ref')
def do_ref(parser, token):
    tag, ref_str = token.split_contents()
    return RefNode(ref_str)


class RefNode(template.Node):

    def __init__(self, ref_str):
        self.ref_str = ref_str
        other, ext = path.splitext(ref_str)
        self.ext = ext[1:]

    def render(self, context):
        return ''

