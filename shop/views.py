from django.shortcuts import render
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt

# For stripe integration
from django.conf import settings
from django.views.generic.base import TemplateView
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def index(request):
    # Fetching all products from database
    #products = Product.objects.all()
    '''
        Now we want list of lists of all different categories. For that we do the following :-
        Step 1.  Get categories of all objects present in database. Dublicate values are also present.
        Step 2.  Apply set comprehension to find unique values of all posible categories.
        STEP 3.  For each item of set (getting from step2) we get all items having same category by
                    applying filter. After that we make list of common category products, range and
                    number of slides required to display common items assuming 4 products in one slide.
    '''
    allprods = []
    catprods = Product.objects.values('category','id')   # STEP 1
    cats = {item['category'] for item in catprods}   # STEP 2
    # STEP 3
    for cat in cats:
        products = Product.objects.filter(category = cat)
        # Calculating number of slides required
        n = len(products)
        nSlides = (n//4) + ceil((n/4)-(n//4))
        allprods.append([products, range(1,nSlides), nSlides])
    params = {'allprods':allprods}
    return render(request,'shop/index.html',params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    query = query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<2:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method == "POST":
        '''
            second argument of get is default value if first argument not present
        '''
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact = Contact(name = name, email = email, phone = phone, desc = desc)
        contact.save()

        # After saving info , we display confirmation msg to user by using javascript.
        received = True;
        return render(request,'shop/contact.html',{'received':received, 'query':desc})
    return render(request,'shop/contact.html')

def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId','')
        email = request.POST.get('email','')
        try:
            order = Orders.objects.filter(order_id = orderId, email = email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id = orderId)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc, 'time':item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request,'shop/tracker.html')


def prViews(request,myid):
    # Fetching the products using id
    product = Product.objects.filter(id = myid)
    return render(request,'shop/prodViews.html',{'product':product[0]})
    # product[0] bcz product is in form of list. So to ease rendering we use product[0]


'''                     Following is used for Stripe payments integration          '''
class CheckOutView(TemplateView):
    template_name = 'shop/checkout.html'

    def get_context_data(self, **kwargs): # new
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

def charge(request):
    """
        We are sending data to Stripe here. We make a charge that includes the amount, currency,
        description, and crucially the source.
        Source has the unique token generated by Stripe for this transaction.
        Then we return the request object and load the charge.html template.
    """
    if request.method == 'POST':
        total_amount = request.POST.get('amount','')
        charge = stripe.Charge.create(
            amount=total_amount,
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        return render(request, 'shop/charge.html')
