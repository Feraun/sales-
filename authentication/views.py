from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

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
                pickup_point=pickup_point,
            )

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product = item['product'],
                                         price = item['price'],
                                         quantity = item['quantity'],
                                         amount_item = item['price'] * item['quantity'])

            cart.clear()

            messages.success(request, "Ваш заказ успешно оформлен!")
            return redirect(request.path)

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
        elif "products" in request.POST:
            return redirect('authentication:mds_products')
        elif "suppliers" in request.POST:
            return redirect('authentication:mds_suppliers')
        elif "pickup_points" in request.POST:
            return redirect('authentication:mds_pickup_points')
        elif "orders" in request.POST:
            return redirect('authentication:mds_orders')
        elif "supports" in request.POST:
            return redirect('authentication:mds_supports')


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

def mds_category_edit(request, category_id):

    if request.method == "POST":
        name = request.POST.get('n')
        describe = request.POST.get('d')

        with connection.cursor() as cursor:
             cursor.execute('CALL edit_category(%s, %s, %s)', [category_id, name, describe])
        #print(name, describe)
        return redirect('authentication:mds_categories')

    category = Category.objects.get(id = category_id)

    return render(request, 'authentication/mds/category_edit.html', {'category': category})

def mds_category_delete(request, category_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_category(%s)', [category_id])
    return redirect('authentication:mds_categories')

@user_passes_test(in_group_managers)
def mds_products(request):
    products = Product.objects.all()

    if request.method == "POST":
        name = request.POST.get('n')
        describe = request.POST.get('d')
        price = request.POST.get('p')
        stock_quantity = request.POST.get('sq')
        category_id = request.POST.get('cid')
        supplier_id = request.POST.get('sid')

        with connection.cursor() as cursor:
             cursor.execute('CALL add_product(%s, %s, %s, %s, %s, %s)', [name, describe, price, stock_quantity, category_id, supplier_id])

        return redirect(request.path)

    # categories = Category.objects.all()
    # suppliers = Supplier.objects.all()

    return render(request, 'authentication/mds/products.html', { 'products': products})

def mds_product_edit(request, product_id):

    if request.method == "POST":
        name = request.POST.get('n')
        describe = request.POST.get('d')
        price = request.POST.get('p')
        stock_quantity = request.POST.get('sq')
        category_id = request.POST.get('cid')
        supplier_id = request.POST.get('sid')

        with connection.cursor() as cursor:
             cursor.execute('CALL edit_product(%s, %s, %s, %s, %s, %s, %s)', [product_id, name, describe, price, stock_quantity, category_id, supplier_id])
        #print(name, describe)
        return redirect('authentication:mds_products')

    product = Product.objects.get(id = product_id)

    return render(request, 'authentication/mds/product_edit.html', {'product': product})

def mds_product_delete(request, product_id):
    order_items = OrderItem.objects.all()

    if OrderItem.objects.filter(product_id=product_id).exists():
        return redirect('authentication:mds_products')
        # Можно передать сообщение в шаблон, если хочешь показать это пользователю
    else:
        with connection.cursor() as cursor:
            cursor.execute('CALL delete_product(%s)', [product_id])
        return redirect('authentication:mds_products')

@user_passes_test(in_group_managers)
def mds_suppliers(request):
    suppliers = Supplier.objects.all()

    if request.method == "POST":
        name = request.POST.get('n')
        contact_info = request.POST.get('ci')
        address = request.POST.get('a')

        with connection.cursor() as cursor:
             cursor.execute('CALL add_supplier(%s, %s, %s)', [name, contact_info, address])

        return redirect(request.path)

    # categories = Category.objects.all()
    # suppliers = Supplier.objects.all()

    return render(request, 'authentication/mds/suppliers.html', { 'suppliers': suppliers })

def mds_supplier_edit(request, supplier_id):

    if request.method == "POST":
        name = request.POST.get('n')
        contact_info = request.POST.get('ci')
        address = request.POST.get('a')

        with connection.cursor() as cursor:
             cursor.execute('CALL edit_supplier(%s, %s, %s, %s)', [supplier_id, name, contact_info, address])
        #print(name, describe)
        return redirect('authentication:mds_suppliers')

    supplier = Supplier.objects.get(id = supplier_id)

    return render(request, 'authentication/mds/supplier_edit.html', {'supplier': supplier})

def mds_supplier_delete(request, supplier_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_supplier(%s)', [supplier_id])
    return redirect('authentication:mds_suppliers')

@user_passes_test(in_group_managers)
def mds_pickup_points(request):
    pickup_points = Pickup_point.objects.all()

    if request.method == "POST":
        address = request.POST.get('a')
        phone = request.POST.get('p')

        with connection.cursor() as cursor:
             cursor.execute('CALL add_pickup_point(%s, %s)', [address, phone])

        return redirect(request.path)

    # categories = Category.objects.all()
    # suppliers = Supplier.objects.all()

    return render(request, 'authentication/mds/pickup_points.html', { 'pickup_points': pickup_points })

def mds_pickup_point_edit(request, pickup_point_id):

    if request.method == "POST":
        address = request.POST.get('a')
        phone = request.POST.get('p')

        with connection.cursor() as cursor:
             cursor.execute('CALL edit_pickup_point(%s, %s, %s)', [pickup_point_id, address, phone])
        #print(name, describe)
        return redirect('authentication:mds_pickup_points')

    pickup_point = Pickup_point.objects.get(id = pickup_point_id)

    return render(request, 'authentication/mds/pickup_point_edit.html', {'pickup_point': pickup_point})

def mds_pickup_point_delete(request, pickup_point_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_pickup_point(%s)', [pickup_point_id])
    return redirect('authentication:mds_pickup_points')

@user_passes_test(in_group_managers)
def mds_orders(request):
    orders = Order.objects.all()
    orders_items = OrderItem.objects.all()

    users = User.objects.all()

    if request.method == "POST":
        return redirect('authentication:mds_order')


    return render(request, 'authentication/mds/orders.html', {'orders': orders, 'orders_items': orders_items})

def mds_order(request, order_id):
    order = Order.objects.get(id = order_id)
    order_items = OrderItem.objects.filter(order = order)

    if request.method == 'POST':
        quantities = request.POST.getlist('quantities')

        for order_item, quantity in zip(order_items, quantities):
            with connection.cursor() as cursor:
                cursor.execute('CALL update_order_item_quantity(%s, %s)', [order_item.id, int(quantity)])

        return redirect(request.path)

    return render(request, 'authentication/mds/order.html', {'order': order ,'order_items': order_items})

def mds_order_delete(request, order_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_order(%s)', [order_id])
    return redirect('authentication:mds_orders')

def mds_supports(request):
    supports = Support.objects.all()

    return render(request, 'authentication/mds/supports.html', {"supports": supports})

def mds_support_delete(request, support_id):
    with connection.cursor() as cursor:
        cursor.execute('CALL delete_support(%s)', [support_id])
    return redirect('authentication:mds_supports')

def reports(request):
    if request.method == 'POST':
        orderitems = (OrderItem.objects
                      .values('product__name', 'product__supplier__name')
                      .annotate(total_sold=Sum('quantity'))
                      .order_by('-total_sold'))

        return render(request,'authentication/mds/reports.html', {'orderitems': orderitems})
    else:
        return render(request, 'authentication/mds/reports.html')