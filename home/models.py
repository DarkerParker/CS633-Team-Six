from django.db import models

from wagtail.core.models import Page

from modelcluster.fields import ParentalKey
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from store.models import Product
class HomePage(Page):
    header = models.CharField(max_length=255,blank=True)
    body = RichTextField(blank=True)
    flavor = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('header'),
        FieldPanel('body', classname="full"),
        FieldPanel('flavor', classname="full")
    ]

    def get_context(self, request):
        context = super().get_context(request)

        products = Product.objects.filter(featured=True).live()
        
        for product in products:
            if product.image:
                etsy_images = [product.image]
            else:
                etsy_images = []
            if product.etsy_images:
                product.etsy_images = product.etsy_images.replace("fullxfull", "300x300")
                etsy_images += product.etsy_images.split("|")
            product.etsy_imgs = etsy_images

        context['products'] = products



        return context

@register_setting
class SnipcartSettings(BaseSetting):
    api_key = models.CharField(
        max_length=255,
        help_text='Your Snipcart public API key'
    )