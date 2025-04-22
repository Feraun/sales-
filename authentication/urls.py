from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('reg', views.sign_up, name='reg'),

    path('login', views.log_in, name='login'),
    path('', views.log_in),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('manager_ds/', views.manager_dashboard, name='manager_dashboard'),

    path('dashboard/make_order', views.make_order, name='make_ord'),
    path('dashboard/make_order/add/<int:product_id>', views.cart_add, name='cart_add'),
    path('dashboard/make_order/remove/<int:product_id>', views.cart_remove, name='cart_remove'),

    path('dashboard/history_of_orders', views.history_of_orders, name='history'),
    path('dashboard/support', views.support, name="support"),

    path('dashboard/logout', views.logout, name='logout'),

    path('manager_ds/categories', views.mds_categories, name='mds_categories'),
    path('manager_ds/categories/delete/<int:category_id>', views.mds_category_delete, name='mds_category_delete')
    # path('cart', views.cart_detail, name='cart_detail'),
    # path('cart/add/<int:product_id>', views.cart_add, name='cart_add'),
    # path('cart/remove/<int:product_id>', views.cart_remove, name='cart_remove'),
]