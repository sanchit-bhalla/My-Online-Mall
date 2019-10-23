from django.shortcuts import render
from django.http import HttpResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
#from PayTm import Checksum
# Create your views here.
MERCHANT_KEY = 'Your-Merchant-Key-Here'


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

def checkout(request):
    if request.method == "POST":
        '''
            second argument of get is default value if first argument not present
        '''
        items_json = request.POST.get('itemsJson','')
        name = request.POST.get('name','')
        amount = request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address1','')+ " " +request.POST.get('address2','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')
        phone = request.POST.get('phone','')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()

        '''
            When order is saved one update is pushed at that time . These updates can be viewed
            by customer in tracker by passing his/her details
        '''
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        thank = True;
        id = order.order_id
        return render(request,'shop/checkout.html',{'thank':thank, 'id':id})
        '''
        # Request the paytm to transfer the amount to your account after payment by user
        param_dict = {
                 'MID':'WorldP64425807474247',
                 'ORDER_ID': str(order.order_id),
                 'TXN_AMOUNT': str(amount),
                 'CUST_ID': email,
                'INDUSTRY_TYPE_ID':'Retail',
                'WEBSITE':'WEBSTAGING',  # WEBSTAGING is used for testing
                'CHANNEL_ID':'WEB',
                # CALLBACK_URL is that where paytm will send post request to us
    	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlepayment/',
        }
        return render(request, 'shop/paytm.html',{'param_dict':param_dict})
        '''
    return render(request,'shop/checkout.html')

"""
    We use this bcz bcz paytm will send post request to us and also a post request is send to paytm
    But due to csrf_token error occurs. So we exempt that
"""

# Watch the code with harry video
@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
