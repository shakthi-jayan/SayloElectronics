from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from shop.models import Product, Category
from .forms import ProductForm, CategoryForm
from .models import AdminLog


from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is staff,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/accounts/login/'
    )
    return actual_decorator(view_func)

def is_admin(user):
    return user.is_authenticated and user.is_staff

def log_admin_action(user, action, model, record_id):
    AdminLog.objects.create(
        user=user,
        action=action,
        model=model,
        record_id=record_id
    )

# Product Views
@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'customadmin/products/list.html', {
        'products': products,
        'active': 'products'
    })

@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            log_admin_action(request.user, 'created', 'Product', product.id)
            messages.success(request, 'Product created successfully!')
            return redirect('customadmin:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'customadmin/products/form.html', {
        'form': form,
        'title': 'Create Product',
        'active': 'products'
    })

@login_required
@user_passes_test(is_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            log_admin_action(request.user, 'updated', 'Product', product.id)
            messages.success(request, 'Product updated successfully!')
            return redirect('customadmin:product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'customadmin/products/form.html', {
        'form': form,
        'title': 'Update Product',
        'active': 'products'
    })

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_id = product.id
        product.delete()
        log_admin_action(request.user, 'deleted', 'Product', product_id)
        messages.success(request, 'Product deleted successfully!')
        return redirect('customadmin:product_list')
    
    return render(request, 'customadmin/products/confirm_delete.html', {
        'product': product,
        'active': 'products'
    })

# Category Views
@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all().order_by('-id')
    return render(request, 'customadmin/categories/list.html', {
        'categories': categories,
        'active': 'categories'
    })

@login_required
@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            log_admin_action(request.user, 'created', 'Category', category.id)
            messages.success(request, 'Category created successfully!')
            return redirect('customadmin:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'customadmin/categories/form.html', {
        'form': form,
        'title': 'Create Category',
        'active': 'categories'
    })

@login_required
@user_passes_test(is_admin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            log_admin_action(request.user, 'updated', 'Category', category.id)
            messages.success(request, 'Category updated successfully!')
            return redirect('customadmin:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'customadmin/categories/form.html', {
        'form': form,
        'title': 'Update Category',
        'active': 'categories'
    })

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category_id = category.id
        category.delete()
        log_admin_action(request.user, 'deleted', 'Category', category_id)
        messages.success(request, 'Category deleted successfully!')
        return redirect('customadmin:category_list')
    
    return render(request, 'customadmin/categories/confirm_delete.html', {
        'category': category,
        'active': 'categories'
    })

# Admin Logs
@login_required
@user_passes_test(is_admin)
def admin_logs(request):
    logs = AdminLog.objects.all().order_by('-timestamp')
    return render(request, 'customadmin/logs.html', {
        'logs': logs,
        'active': 'logs'
    })
# customadmin/views.py
from shop.models import Order

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all().order_by('-created_at')[:5]
    categories = Category.objects.all()
    orders = Order.objects.all().order_by('-created_at')[:5]
    return render(request, 'customadmin/dashboard.html', {
        'products': products,
        'categories': categories,
        'orders': orders,
        'active': 'dashboard'
    })
# customadmin/views.py
@login_required
@user_passes_test(is_admin)
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'customadmin/orders/list.html', {
        'orders': orders,
        'active': 'orders'
    })

@login_required
@user_passes_test(is_admin)
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'customadmin/orders/detail.html', {
        'order': order,
        'active': 'orders'
    })

@login_required
@user_passes_test(is_admin)
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Order.STATUS_CHOICES]:
            order.status = new_status
            order.save()
            log_admin_action(request.user, 'updated', 'Order status', order.id)
            messages.success(request, 'Order status updated successfully!')
        else:
            messages.error(request, 'Invalid status!')
    return redirect('customadmin:order_detail', pk=order.id)