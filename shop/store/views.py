from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import FileSystemStorage
from django.db.models import F
from .models import Product, Vest, Order, OrderItem, CartItem
from datetime import datetime


# Проверка на администратора
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# Главная
def index(request):
    return render(request, 'index.html')


# Страница "О нас"
def about(request):
    return render(request, 'about.html')


# Регистрация
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь уже существует")
        else:
            user = User.objects.create_user(username=username, password=password)
            messages.success(request, "Регистрация успешна")
            return redirect('login')
    return render(request, 'register.html')


# Логин
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Вход выполнен")
            return redirect('index')
        else:
            messages.error(request, "Неверные данные")
    return render(request, 'login.html')


# Логаут
def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из системы")
    return redirect('login')


# Профиль
@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


# Продукты
def products_view(request):
    products = Product.objects.all()
    caliber = request.GET.get('caliber', '').strip()
    ammo_type = request.GET.get('ammo_type', '').strip()
    if caliber:
        products = products.filter(caliber__icontains=caliber)
    if ammo_type:
        products = products.filter(ammo_type__icontains=ammo_type)
    return render(request, 'products.html', {'items': products})


# Добавление продукта
@admin_required
def add_product_view(request):
    if request.method == 'POST':
        caliber = request.POST['caliber']
        ammo_type = request.POST['ammo_type']
        designation = request.POST['designation']
        penetration = request.POST['penetration']
        fragmentation = request.POST['fragmentation']
        price = request.POST['price']
        description = request.POST.get('description', '')
        availability_status = request.POST.get('availability_status', 'in_stock')
        restock_hours = request.POST.get('restock_hours') or None
        if restock_hours:
            restock_hours = int(restock_hours)
        image = request.FILES.get('image')
        product = Product.objects.create(
            caliber=caliber, ammo_type=ammo_type, designation=designation,
            penetration=penetration, fragmentation=fragmentation,
            price=price, description=description, availability_status=availability_status,
            restock_hours=restock_hours, image=image
        )
        messages.success(request, "Патрон добавлен")
        return redirect('products')
    return render(request, 'add_product.html')


# Удаление продукта
@admin_required
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, "Товар удалён")
    return redirect('products')


# Корзина продуктов
@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'cart.html', {'items': items, 'total': total})


# Добавление в корзину продукта
@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, "Добавлено в корзину")
    return redirect('cart')


# Удаление из корзины продукта
@login_required
def remove_from_cart_view(request, cart_id):
    cart_item = get_object_or_404(CartItem, pk=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Товар удалён из корзины")
    return redirect('cart')


# Оформление заказа продуктов
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Корзина пуста!")
        return redirect('cart')

    order = Order.objects.create(user=request.user)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_time=item.product.price,
            item_type='product'
        )

    cart_items.delete()
    messages.success(request, "Заказ успешно оформлен!")
    return redirect('order_history')  # 👈 правильное имя


# История заказов
@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})


# Бронежилеты
def vests_view(request):
    items = Vest.objects.all()
    return render(request, 'vests.html', {'items': items})


@admin_required
def add_vest_view(request):
    if request.method == 'POST':
        model = request.POST['model']
        protection_level = request.POST['protection_level']
        weight = float(request.POST['weight'])
        price = float(request.POST['price'])
        description = request.POST.get('description', '')
        availability_status = request.POST.get('availability_status', 'in_stock')
        restock_hours = request.POST.get('restock_hours') or None
        image = request.FILES.get('image')
        Vest.objects.create(
            model=model, protection_level=protection_level, weight=weight,
            price=price, description=description, availability_status=availability_status,
            restock_hours=restock_hours, image=image
        )
        messages.success(request, "Бронежилет добавлен")
        return redirect('vests')
    return render(request, 'add_vest.html')


@admin_required
def delete_vest_view(request, vest_id):
    vest = get_object_or_404(Vest, pk=vest_id)
    vest.delete()
    messages.success(request, "Бронежилет удалён")
    return redirect('vests')


# Корзина бронежилетов через сессии
def add_vest_to_cart_view(request, vest_id):
    cart = request.session.get('cart_vests', [])
    if vest_id not in cart:
        cart.append(vest_id)
    request.session['cart_vests'] = cart
    messages.success(request, "Бронежилет добавлен в корзину")
    return redirect('cart_vests')


def cart_vests_view(request):
    cart = request.session.get('cart_vests', [])
    items = Vest.objects.filter(id__in=cart)
    return render(request, 'cart_vests.html', {'items': items})


@login_required
def checkout_vests_view(request):
    cart = request.session.get('cart_vests', [])
    if not cart:
        messages.error(request, "Корзина пуста")
        return redirect('vests')
    order = Order.objects.create(user=request.user, created_at=datetime.now())
    for vest_id in cart:
        vest = get_object_or_404(Vest, pk=vest_id)
        OrderItem.objects.create(
            order=order, vest=vest, quantity=1,
            price_at_time=vest.price, item_type='vest'
        )
    request.session['cart_vests'] = []
    messages.success(request, "Заказ бронежилетов оформлен")
    return redirect('order_history')


def remove_vest_from_cart_view(request, vest_id):
    cart = request.session.get('cart_vests', [])
    cart = [v for v in cart if v != vest_id]
    request.session['cart_vests'] = cart
    messages.success(request, "Бронежилет удалён из корзины")
    return redirect('cart_vests')


@login_required
def update_cart_view(request, cart_id):
    cart_item = get_object_or_404(CartItem, pk=cart_id, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()  # если 0 — удаляем из корзины
    return redirect('cart')
