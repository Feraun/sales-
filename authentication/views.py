from itertools import product

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Product, Order, Pickup_point, Cart, Support, OrderItem
from .forms import CartAddProductForm
from .cart import Cart

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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Выполняем вход
            return redirect('authentication:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "authentication/login.html", {"form":form})

def logout(request):
    if request.method == 'POST':
        return redirect('authentication:login')

@login_required
def dashboard(request):
    products = Product.objects.all()

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

    return render(request, 'authentication/dashboard.html', {'products': products})

@login_required
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

@login_required
def history_of_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id = user_id)
    orders_item = OrderItem.objects.filter(order__in = orders)

    return render(request, 'authentication/history_of_orders.html', {'orders': orders, 'orders_item': orders_item})

@login_required
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


# def cart_detail(request):
#     cart = Cart(request)
#     return render(request, 'authentication/detail.html', {'cart': cart})
