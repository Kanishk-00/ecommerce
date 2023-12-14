from django.shortcuts import render
from django.views import View
from . models import Product
from django.shortcuts import redirect
from django.db.models import Count
from . forms import CustomerRegistrationForm , CustomerProfileForm
from django.contrib import messages
from .models import Customer, Cart, Payment
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.db.models import Q
import razorpay
from django.conf import settings

# Create your views here.
def home(req):
    return render(req, "app/home.html")


def about(req):
    return render(req, "app/about.html")


def contact(req):
    return render(req, "app/contact.html")

class CategoryView(View):
    def get(self, request, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        return render(request, "app/category.html", locals())

class CategoryTitle(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "app/category.html", locals())

class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, 'app/productdetail.html', locals())
    

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', locals())
    
    def post(self, request):
        print("the request is here: ", request)
        form = CustomerRegistrationForm(request.POST)
        if(form.is_valid()):
            form.save()
            messages.success(request, "Congratulations! User Register successfully")
        else:
            messages.warning(request, "Invalid Input data")
        return render(request, 'app/customerregistration.html', locals())
    

class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', locals())
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if(form.is_valid()):
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user = user, name = name, locality = locality, mobile = mobile, city = city, state = state, zipcode = zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profiled Saved Successfully")
        else:
            messages.warning(request, "Invalid Input Data")

        return render(request, 'app/profile.html', locals())



def address(request):
    add = Customer.objects.filter(user = request.user)
    return render(request, 'app/address.html', locals())


class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk = pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html', locals())
    def post(self, request, pk):
        form = CustomerProfileForm(request.POST) 
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile Updated Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")  
    
    

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    try:
        product_id = int(product_id)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid product ID")

    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user = user)
    amount = 0
    for p in cart:
        value = p.quantity*(p.product.discounted_price)
        amount = amount + value
    totalamount = amount + 40
    return render(request, "app/addtocart.html", locals())



def plus_cart(request):
    if(request.method == "GET"):
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
        c.quantity += 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user = user)
        amount = 0
        for p in cart:
            value = p.quantity*(p.product.discounted_price)
            amount = amount + value
        totalamount = amount + 40
        print(prod_id)
        data = {
            'quantity' : c.quantity, 
            'amount' : amount, 
            'totalamount' : totalamount
        }
        return JsonResponse(data)




def minus_cart(request):
    if(request.method == 'GET'):
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
        c.quantity -= 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user = user)
        amount = 0
        for p in cart:
            value = p.quantity*(p.product.discounted_price)
            amount = amount + value
        totalamount = amount + 40
        data = {
            'quantity' : c.quantity, 
            'amount' : amount, 
            'totalamount' : totalamount, 
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user = user)
        amount = 0
        for p in cart:
            value = p.quantity*(p.product.discounted_price)
            amount = amount + value
        totalamount = amount + 40
        data = {
            'amount' : amount, 
            'totalamount' : totalamount
        }
        return JsonResponse(data)
    


class checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user = user)
        cart_items = Cart.objects.filter(user = user)
        famount = 0
        for p in cart_items:
            value = p.quantity*(p.product.discounted_price)
            famount = famount + value
        totalamount = famount + 40
        razorpayamount = int(totalamount*100)
        client = razorpay.Client(auth = (settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {'amount' : razorpayamount, 'currency' : "INR", "receipt" : "order_rcptid_11"}
        payment_response = client.order.create(data=data)
        print("the payment response is", payment_response)
        # the payment response is {'id': 'order_NCGfbY886Nv3wu', 'entity': 'order', 'amount': 91500, 'amount_paid': 0, 'amount_due': 91500, 'currency': 'INR', 'receipt': 'order_rcptid_11', 'offer_id': None, 'status': 'created', 'attempts': 0, 'notes': [], 'created_at': 1702566180}
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user = user, 
                amount = totalamount, 
                razorpay_order_id = order_id, 
                razorpay_payment_status = order_status
            )
            payment.save()
        return render(request, 'app/checkout.html', locals()) 
    

# new
    
