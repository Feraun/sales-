from pydoc import describe

from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.views.decorators.http import require_POST

from .models import Product, Order, Pickup_point, Cart, Support, OrderItem, Category, Supplier
from .forms import CartAddProductForm
from .cart import Cart

def in_group_buyers(user):
    return user.groups.filter(name='Buyers').exists()

def in_group_managers(user):
    return user.groups.filter(name='Managers').exists()

# Create your views here.
def sign_up(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('authentication:login')
    else:
        form = UserCreationForm()
    return render(request, "authentication/register.html", {"form":form})

def log_in(request):
    if request.method == 'POST':
        
        if "login" in request.POST:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()

                login(request, user)

                if in_group_buyers(user):
                    return redirect('authentication:dashboard')
                if in_group_managers(user):
                    return redirect('authentication:manager_dashboard')

        if "registration" in request.POST:
            return redirect('authentication:reg') 

    else:
        form = AuthenticationForm()
    return render(request, "authentication/login.html", {"form":form})

def logout(request):
    if request.method == 'POST':
        return redirect('authentication:login')

@user_passes_test(in_group_buyers)
def dashboard(request):

    if request.method == 'POST':
        if "logout" in request.POST:
            auth.logout(request)
            return render(request, 'authentication/logout.html')
        if "make_order" in request.POST:
            return redirect('authentication:make_ord')
        if "history_of_orders" in request.POST:
            return redirect('authentication:history')
        if "support" in request.POST:
            return redirect('authentication:support')

    return render(request, 'authentication/dashboard.html')

@user_passes_test(in_group_buyers)
def make_order(request):
    cart = Cart(request)

    if request.method == "POST":
        if "make_ord" in request.POST:

            pickup_point_id = request.POST.get('pickup_point_id')
            pickup_point = Pickup_point.objects.get(id = pickup_point_id)

            order = Order.objects.create(
                user_id=request.user.id,
                amount=cart.get_total_price(),
                pickup_point=pickup_point.address,
            )

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product = item['product'],
                                         price = item['price'],
                                         quantity = item['quantity'])

            cart.clear()

            messages.success(request, "Ваш заказ успешно оформлен!")
            return redirect(request.path)

            # product_id = request.POST.get('product_id')
            # quantity_str = request.POST.get('quantity', '1')
            #
            #
            # try:
            #     quantity = int(quantity_str)
            # except ValueError:
            #     quantity = 1
            #
            # product = Product.objects.get(id=product_id)
            # total_amount = product.price * quantity
            #
            # pickup_point = Pickup_point.objects.get(id = pickup_point_id)
            #
            #
            #
            # messages.success(request, "Ваш заказ успешно оформлен!")
            # return redirect(request.path)  # PRG: перенаправляем на тот же URL

    products = Product.objects.all()
    pickup_points = Pickup_point.objects.all()

    cart_product_form = CartAddProductForm()

    cart = Cart(request)

    return render(request, 'authentication/make_order.html', {
        'products': products,
        'pickup_points': pickup_points,
        'cart_product_form': cart_product_form,
        'cart': cart,
    }
    )

@user_passes_test(in_group_buyers)
def history_of_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id = user_id)
    orders_item = OrderItem.objects.filter(order__in = orders)

    return render(request, 'authentication/history_of_orders.html', {'orders': orders, 'orders_item': orders_item})

@user_passes_test(in_group_buyers)
def support(request):

    if request.method == "POST":

        text_complaint = request.POST.get('text')

        Support.objects.create(
            user_id=request.user.id,
            text_complaint = text_complaint,
        )

        messages.success(request, "Ваш обращение успешно отправлено!")
        return redirect(request.path)  # PRG: перенаправляем на тот же URL

    supports = Support.objects.filter(user_id = request.user.id)

    return render(request, 'authentication/support.html', {'supports': supports})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(Product, id = product_id)

    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data

        cart.add(product = product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])

        return redirect('authentication:make_ord')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('authentication:make_ord')


@user_passes_test(in_group_managers)
def manager_dashboard(request):
    # products = Product.objects.all()
    # orders = Order.objects.all()
    # categorys = Category.objects.all()
    # pickup_points = Pickup_point.objects.all()
    # order_items = OrderItem.objects.all()
    # supports = Support.objects.all()
    # suppliers = Supplier.objects.all()
    if request.method == 'POST':
        # if "logout" in request.POST:
        #     auth.logout(request)
        #     return render(request, 'authentication/logout.html')
        if "categories" in request.POST:
            return redirect('authentication:mds_categories')


    return render(request, 'authentication/manager_dashboard.html')

@user_passes_test(in_group_managers)
def mds_categories(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get('n')
        describe = request.POST.get('d')

        with connection.cursor() as cursor:
             cursor.execute('CALL add_category(%s, %s)', [name, describe])
        #print(name, describe)
        return redirect(request.path)

    return render(request, 'authentication/mds/categories.html', {'categories': categories})

def mds_category_delete(request, category_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_category(%s)', [category_id])
    return redirect('authentication:mds_categories')

# def cart_detail(request):
#     cart = Cart(request)
#     return render(request, 'authentication/detail.html', {'cart': cart})