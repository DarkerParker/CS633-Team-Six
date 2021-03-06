from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from wagtail.core.models import Page
from wagtail.search.models import Query
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from store.models import ShopPage, Product, ProductCustomField
import csv
import io
from django.utils.text import slugify
import random



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
            store_page = ShopPage.objects.all().live()[0]
            for item in data:
                try:
                    title = item['TITLE']
                    description = item['DESCRIPTION']
                    price = item['PRICE']
                    quantity = item['QUANTITY']
                    sku = item['SKU']
                    if sku == "":
                        sku = str(random.randint(1, 9999999))
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
                    if item['VARIATION 1 NAME'] != "":
                        options = ProductCustomField(product=product, options=item['VARIATION 1 VALUES'].replace(",","|"), name=item['VARIATION 1 NAME'])
                        options.save()
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

def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        search_results = Product.objects.live().search(search_query)
        query = Query.get(search_query)
        # Record hit
        query.add_hit()
    else:
        search_results = Product.objects.all()

    for product in search_results:
        # if product.image:
        #     etsy_images = [request.get_host() + "/static/" + product.image]
        # else:
        etsy_images = []
        if product.etsy_images:
            product.etsy_images = product.etsy_images.replace("fullxfull", "300x300")
            etsy_images += product.etsy_images.split("|")
            product.etsy_imgs = etsy_images

    print(search_results)
    # Pagination
    paginator = Paginator(search_results, 20)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })
