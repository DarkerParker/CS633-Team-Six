from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from wagtail.core.models import Page
from wagtail.search.models import Query
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from store.models import ShopPage, Product
import csv
import io
from django.utils.text import slugify

@login_required(login_url='/django-admin')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # handle_uploaded_file(request.FILES['file'])
            # Read csv file InMemoryUploadedFile
            file = request.FILES['file'].read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file))

            # Generate a list comprehension
            data = [line for line in reader]
            store_page = ShopPage.objects.all()[0]
            for item in data:
                try:
                    title = item['TITLE']
                    description = item['DESCRIPTION']
                    price = item['PRICE']
                    quantity = item['QUANTITY']
                    sku = item['SKU']
                    etsy_images = ""
                    for key in item:
                        if 'IMAGE' in key:
                            if item[key] != "":
                                etsy_images += item[key] + "|"
                    etsy_images = etsy_images[:-1]
                    existing_product = Product.objects.all().filter(slug=slugify(title))
                    if existing_product:
                        existing_product.delete()
                    product = Product(title=title, short_description=description, sku=sku, price=price, quantity=quantity, etsy_images=etsy_images, slug=slugify(title))
                    store_page.add_child(instance=product)
                    store_page.save()
                except Exception as e:
                    print(e)
                    pass
            return HttpResponseRedirect('/etsyuploadsuccess')
    else:
        form = UploadFileForm()
    return render(request, 'search/upload.html', {'form': form})

@login_required(login_url='/django-admin')
def success(request):
    return render(request, 'search/success.html')
