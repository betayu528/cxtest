from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import markdown as markdown_lib

from knowledge.models import ArticleContentFormat

register = template.Library()


@register.filter
def render_article(content, content_format):
    if content_format == ArticleContentFormat.RICHTEXT:
        return mark_safe(content)
    rendered = markdown_lib.markdown(
        escape(content),
        extensions=["fenced_code", "tables", "nl2br"],
    )
    return mark_safe(rendered)
