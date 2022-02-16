from django.db import models

from wagtail.core.models import Page

from modelcluster.fields import ParentalKey
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page, Orderable
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting

class ShopPage(Page):
    header = RichTextField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('header', classname="full"),
        FieldPanel('body', classname="full"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        products = Product.objects.live()
        for product in products:
            etsy_images = []
            if product.etsy_images:
                product.etsy_images = product.etsy_images.replace("fullxfull", "300x300")
                etsy_images += product.etsy_images.split("|")
                product.etsy_imgs = etsy_images
        context['products'] = products

        return context

class Product(Page):
    def get_context(self, request):
        context = super().get_context(request)
        fields = []
        for f in self.custom_fields.get_object_list():
            if f.options:
                f.options_array = f.options.split('|')
                fields.append(f)
            else:
                fields.append(f)

        context['custom_fields'] = fields
        if self.image:
            etsy_images = [self.image]
        else:
            etsy_images = []
        if self.etsy_images:
            self.etsy_images = self.etsy_images
            etsy_images += self.etsy_images.split("|")
        context['etsy_imgs'] = etsy_images

        return context
    sku = models.CharField(max_length=255)
    quantity = models.IntegerField(blank=False, null=False)
    short_description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    featured = models.BooleanField(default=False)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    etsy_images = models.CharField(max_length=5000, blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('sku'),
        FieldPanel('price'),
        FieldPanel('quantity'),
        ImageChooserPanel('image'),
        FieldPanel('featured'),
        FieldPanel('short_description'),
        FieldPanel('etsy_images'),
        InlinePanel('custom_fields', label='Custom fields'),
    ]

class ProductCustomField(Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='custom_fields')
    name = models.CharField(max_length=255)
    options = models.CharField(max_length=500, null=True, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('options')
    ]
