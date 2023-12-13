from django.shortcuts import render
from django.views import View
from . models import Product
from django.db.models import Count
from . forms import CustomerRegistrationForm , CustomerProfileForm
from django.contrib import messages
from .models import Customer

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
