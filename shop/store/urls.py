from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),

    # Пользователи
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Продукты
    path('products/', views.products_view, name='products'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('delete_product/<int:product_id>/', views.delete_product_view, name='delete_product'),

    # Корзина продуктов
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('remove_from_cart/<int:cart_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),

    # История заказов
    path('orders/', views.order_history_view, name='order_history'),

    # Бронежилеты
    path('vests/', views.vests_view, name='vests'),
    path('add_vest/', views.add_vest_view, name='add_vest'),
    path('delete_vest/<int:vest_id>/', views.delete_vest_view, name='delete_vest'),

    # Корзина бронежилетов через сессии
    path('add_vest_to_cart/<int:vest_id>/', views.add_vest_to_cart_view, name='add_vest_to_cart'),
    path('cart_vests/', views.cart_vests_view, name='cart_vests'),
    path('checkout_vests/', views.checkout_vests_view, name='checkout_vests'),
    path('remove_vest_from_cart/<int:vest_id>/', views.remove_vest_from_cart_view, name='remove_vest_from_cart'),
    path('update_cart/<int:cart_id>/', views.update_cart_view, name='update_cart'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
