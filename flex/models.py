"""Flexible page."""
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField

class FlexPage(Page):
    """Flexibile page class."""

    template = "flex/flex_page.html"

    # @todo add streamfields 
    # content = StreamField()

    first_paragraph = RichTextField(blank=True)
    second_paragraph = RichTextField(blank=True)
    third_paragraph = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("first_paragraph"),
        FieldPanel("second_paragraph"),
        FieldPanel("third_paragraph"),
    ]

    class Meta:  # noqa 
        verbose_name = "Flex Page"
        verbose_name_plural = "Flex Pages"