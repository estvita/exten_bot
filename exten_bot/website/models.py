from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtailcodeblock.blocks import CodeBlock


class ArticlePage(Page):
    menu_title = models.CharField(blank=True, max_length=150)
    body = StreamField(
        [
            ("rich_text", RichTextBlock()),
            ("code", CodeBlock(label="Code")),
        ],
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("menu_title"),
    ]

    def get_menu_title(self):
        return self.menu_title if self.menu_title else self.title
