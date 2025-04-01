from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('reg', views.sign_up, name='reg'),
    path('login', views.log_in, name='login'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('dashboard/make_order', views.make_order, name='make_ord'),
    path('dashboard/make_order/add/<int:product_id>', views.cart_add, name='cart_add'),
    path('dashboard/make_order/remove/<int:product_id>', views.cart_remove, name='cart_remove'),

    path('dashboard/history_of_orders', views.history_of_orders, name='history'),

    path('dashboard/support', views.support, name="support"),

    path('dashboard/logout', views.logout, name='logout'),
    # path('cart', views.cart_detail, name='cart_detail'),
    # path('cart/add/<int:product_id>', views.cart_add, name='cart_add'),
    # path('cart/remove/<int:product_id>', views.cart_remove, name='cart_remove'),
]