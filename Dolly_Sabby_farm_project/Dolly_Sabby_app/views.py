from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import *
from . import forms
from Dolly_Sabby_app.forms import UserForm, UserProfileInfoForm
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse,reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import *
from .forms import *
# from django.core.urlresolvers import reverse
# Create your views here.


# View,TemplateView,CreateView,FormView,DetailView,ListView

#class

class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)

class IndexView(TemplateView):
    template_name = 'index.html'

class ProductView(EcomMixin, TemplateView):
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = Product.objects.all().order_by("-id")
        paginator = Paginator(all_products, 4)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['product_list'] = product_list
        return context

class ProductDetailsView(EcomMixin, TemplateView):
    template_name = 'product_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context

class AddToCartView(EcomMixin, TemplateView):
    template_name = 'add_to_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #get product id from request
        product_id = self.kwargs['pro_id']

        #get product
        product_obj = Product.objects.get(id=product_id)

        #check if the cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)

            #items already exists in the cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity +=1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            #new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        #check if product already exists in cart
        return context

class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        cart_id = request.session.get("cart_id", None)
        # if cart_id:
        #     cart2 = Cart.objects.get(id=cart_id)
        #     if cart1 != cart2:
        #         return redirect("Dolly_Sabby_app:my_cart")
        # else:
        #     return redirect("Dolly_Sabby_app:my_cart")
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action =="rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("Dolly_Sabby_app:my_cart")

class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("Dolly_Sabby_app:my_cart")

class MyCartView(EcomMixin, TemplateView):
    template_name = 'my_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

class CheckoutView(EcomMixin, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("Dolly_Sabby_app:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Khalti":
                return redirect(reverse("Dolly_Sabby_app:khaltipayment") + "?o_id=" + str(order.id))
            elif pm == "PayPal":
                return redirect(reverse("Dolly_Sabby_app:paypal") + "?o_id=" + str(order.id))
        else:
            return redirect("Dolly_Sabby_app:index")
        return super().form_valid(form)

# payments methods
class KhaltiPaymentView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {"order":order}

        return render(request, "khalti_payment.html",context)

class PaypalPaymentView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {"order":order}

        return render(request, "paypal_payment.html",context)

class CustomerRegistrationView(CreateView):
    template_name = "customers_registration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("Dolly_Sabby_app:index")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("Dolly_Sabby_app:index")

class CustomerLoginView(FormView):
    template_name = "customers_login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("Dolly_Sabby_app:index")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class,"error":"Invalid credentials"})
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerProfileView(TemplateView):
    template_name = "customer_profile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context

class CustomerOrderDetailView(DetailView):
    template_name = "customer_order_detail.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("Dolly_Sabby_app:profile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # kw = self.request.GET["keyword"]
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw))
        context["results"] = results
        return context


#Admin pages
class AdminLoginView(FormView):
    template_name = "admin_pages/admin_login.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("Dolly_Sabby_app:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class,"error":"Invalid credentials"})

        return super().form_valid(form)


class AdminRequiredMix(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/adminlogin/")
        return super().dispatch(request, *args, **kwargs)

class AdminHomeView(AdminRequiredMix,TemplateView):
    template_name = "admin_pages/admin_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context

class AdminOrderDetailView(AdminRequiredMix,DetailView):
    template_name = "admin_pages/admin_order_detail.html"
    model = Order
    context_object_name = "ord_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context



class AdminOrderListView(AdminRequiredMix,ListView):
    template_name = "admin_pages/admin_order_list.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"

class AdminOrderStatusView(AdminRequiredMix, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("Status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("Dolly_Sabby_app:adminorderdetail", kwargs={"pk": order_id}))

#link html with django
# def index(request):
#     return render(request,'index.html')

# def product(request):
#     product = models.Product()
#
#     return render(request,'product.html')

# def product_details(request):
#     return render(request,'product_details.html')

# def Cart(request):
#     return render(request,'cart.html')

def index2(request):#function
    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            registered = True

        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()



    return render(request,'index2.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered})

#form
def form_name_view(request):
    form = forms.FormName()

    if request.method == "POST":
        form = forms.FormName(request.POST)

        if form.is_valid():
            #DO SOMETHING CODE
            print("VALIDATION SUCCESS!")
            print("NAME: "+form.cleaned_data['name'])
            print("EMAIL: "+form.cleaned_data['email'])
            print("TEXT: "+form.cleaned_data['text'])

    return render(request,'index.html',{'form':form})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST>get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))

            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")

        else:
            print("Someone tried to login and failed!")
            print("Username: {} and password {}".format(username,password))
            return   HttpResponse("invalid login details supplied!")
    else:
        return render(request,'index2.html',{})

@login_required
def special(request):
    return HttpResponse("You are logged in, Nice!")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
