from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('reg', views.sign_up, name='reg'),

    path('login', views.log_in, name='login'),
    path('', views.log_in),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('dashboard/make_order', views.make_order, name='make_ord'),
    path('dashboard/make_order/add/<int:product_id>', views.cart_add, name='cart_add'),
    path('dashboard/make_order/remove/<int:product_id>', views.cart_remove, name='cart_remove'),

    path('dashboard/history_of_orders', views.history_of_orders, name='history'),
    path('dashboard/support', views.support, name="support"),

    path('dashboard/logout', views.logout, name='logout'),



    path('manager_ds/', views.manager_dashboard, name='manager_dashboard'),

    path('manager_ds/categories', views.mds_categories, name='mds_categories'),
    path('manager_ds/categories/edit/<int:category_id>', views.mds_category_edit, name='mds_category_edit'),
    path('manager_ds/categories/delete/<int:category_id>', views.mds_category_delete, name='mds_category_delete'),

    path('manager_ds/products', views.mds_products, name='mds_products'),
    path('manager_ds/products/edit/<int:product_id>', views.mds_product_edit, name='mds_product_edit'),
    path('manager_ds/products/delete/<int:product_id>', views.mds_product_delete, name='mds_product_delete'),

    path('manager_ds/suppliers', views.mds_suppliers, name='mds_suppliers'),
    path('manager_ds/suppliers/edit/<int:supplier_id>', views.mds_supplier_edit, name='mds_supplier_edit'),
    path('manager_ds/suppliers/delete/<int:supplier_id>', views.mds_supplier_delete, name='mds_supplier_delete'),

    path('manager_ds/pickup_points', views.mds_pickup_points, name='mds_pickup_points'),
    path('manager_ds/pickup_point/edit/<int:pickup_point_id>', views.mds_pickup_point_edit, name='mds_pickup_point_edit'),
    path('manager_ds/pickup_point/delete/<int:pickup_point_id>', views.mds_pickup_point_delete, name='mds_pickup_point_delete'),

    path('manager_ds/orders', views.mds_orders, name='mds_orders'),
    path('manager_ds/order/<int:order_id>', views.mds_order, name='mds_order'),
    path('manager_ds/order/delete/<int:order_id>', views.mds_order_delete, name='mds_order_delete'),

    path('manager_ds/supports', views.mds_supports, name='mds_supports'),
    path('manager_ds/support/delete/<int:support_id>', views.mds_support_delete, name='mds_support_delete')

    # path('cart', views.cart_detail, name='cart_detail'),
    # path('cart/add/<int:product_id>', views.cart_add, name='cart_add'),
    # path('cart/remove/<int:product_id>', views.cart_remove, name='cart_remove'),
]