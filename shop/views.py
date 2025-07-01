from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Cart, Wishlist, Order, OrderItem
from django.contrib import messages
from .forms import CheckoutForm
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def home(request):
    products = Product.objects.filter(stock_quantity__gt=0)
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    in_cart = False
    in_wishlist = False
    
    if request.user.is_authenticated:
        in_cart = Cart.objects.filter(user=request.user, product=product).exists()
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart!')
    return redirect('shop:cart_view')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from cart!')
    return redirect('shop:cart_view')

@login_required
def increase_quantity(request, cart_item_id):
    """Increase the quantity of a cart item by 1"""
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Quantity updated for {cart_item.product.name}')
    return redirect('shop:cart_view')

@login_required
def decrease_quantity(request, cart_item_id):
    """Decrease the quantity of a cart item by 1, remove if quantity becomes 0"""
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f'Quantity updated for {cart_item.product.name}')
        else:
            # Remove item when quantity becomes 0
            product_name = cart_item.product.name
            cart_item.delete()
            messages.info(request, f'{product_name} removed from cart')
    
    return redirect('shop:cart_view')

# Keep the old update_cart for backward compatibility (optional)
@login_required
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('shop:cart_view')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    # Calculate line totals for each item
    for item in cart_items:
        item.line_total = item.product.price * item.quantity
    total = sum(item.line_total for item in cart_items)
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

# AJAX versions for better user experience (optional)
@login_required
def ajax_increase_quantity(request, cart_item_id):
    """AJAX version to increase quantity without page reload"""
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
        cart_item.quantity += 1
        cart_item.save()
        
        # Calculate new totals
        line_total = cart_item.quantity * cart_item.product.price
        cart_total = sum(item.quantity * item.product.price for item in Cart.objects.filter(user=request.user))
        
        return JsonResponse({
            'success': True,
            'new_quantity': cart_item.quantity,
            'line_total': float(line_total),
            'cart_total': float(cart_total)
        })
    return JsonResponse({'success': False})

@login_required
def ajax_decrease_quantity(request, cart_item_id):
    """AJAX version to decrease quantity without page reload"""
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            
            line_total = cart_item.quantity * cart_item.product.price
            cart_total = sum(item.quantity * item.product.price for item in Cart.objects.filter(user=request.user))
            
            return JsonResponse({
                'success': True,
                'new_quantity': cart_item.quantity,
                'line_total': float(line_total),
                'cart_total': float(cart_total),
                'removed': False
            })
        else:
            # Remove item when quantity becomes 0
            cart_item.delete()
            cart_total = sum(item.quantity * item.product.price for item in Cart.objects.filter(user=request.user))
            
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_total': float(cart_total)
            })
    
    return JsonResponse({'success': False})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    return redirect('shop:wishlist_view')

@login_required
def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, pk=wishlist_item_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'{product_name} removed from wishlist!')
    return redirect('shop:wishlist_view')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def checkout(request):
    logger.info(f"Checkout view called by user: {request.user.username}")
    
    # Get cart items
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('shop:cart_view')
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    logger.info(f"Cart total: {total}")
    
    if request.method == 'POST':
        logger.info("Processing POST request for checkout")
        
        try:
            # Create order directly from POST data instead of using form
            order = Order.objects.create(
                user=request.user,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                address_line_1=request.POST.get('address_line_1', ''),
                address_line_2=request.POST.get('address_line_2', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                postal_code=request.POST.get('postal_code', ''),
                country=request.POST.get('country', ''),
                special_instructions=request.POST.get('special_instructions', ''),
                total_amount=total,
                status='pending'  # Make sure status is set
            )
            
            logger.info(f"Order created successfully with ID: {order.id}")
            
            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
                logger.info(f"Created order item: {order_item.id} for product: {cart_item.product.name}")
                
                # Update product stock
                product = cart_item.product
                if product.stock_quantity >= cart_item.quantity:
                    product.stock_quantity -= cart_item.quantity
                    product.save()
                    logger.info(f"Updated stock for {product.name}: {product.stock_quantity}")
                else:
                    logger.warning(f"Insufficient stock for {product.name}")
            
            # Clear the cart
            cart_items.delete()
            logger.info("Cart cleared successfully")
            
            # Pass the order to template for confirmation display
            messages.success(request, f"Order #{order.id} placed successfully! We will contact you soon.")
            
            return render(request, 'shop/checkout.html', {
                'order': order,
                'cart_items': [],
                'total': 0
            })
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            messages.error(request, "There was an error processing your order. Please try again.")
            return render(request, 'shop/checkout.html', {
                'cart_items': cart_items,
                'total': total
            })
    
    # GET request - show checkout form
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})
# Add these views to your existing views.py file

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def about_us(request):
    """
    View for About Us page
    """
    context = {
        'title': 'About Us - Saylo Electronics',
    }
    return render(request, 'shop/about.html', context)

def contact(request):
    """
    View for Contact page with form handling
    """
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate required fields
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'contact.html', {'title': 'Contact Us - Saylo Electronics'})
        
        try:
            # Create email content
            email_subject = f"Contact Form: {subject}"
            email_message = f"""
New contact form submission from Saylo Electronics website:

Name: {name}
Email: {email}
Phone: {phone}
Subject: {subject}

Message:
{message}

---
This message was sent from the Saylo Electronics contact form.
            """
            
            # Send email (optional - configure your email settings)
            # Uncomment the lines below if you want to send emails
            # send_mail(
            #     email_subject,
            #     email_message,
            #     email,  # From email
            #     ['SayloElectronicselectricproducts@gmail.com'],  # To email
            #     fail_silently=False,
            # )
            
            # For now, just show success message
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('shop:contact')
            
        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again.')
            return render(request, 'contact.html', {'title': 'Contact Us - Saylo Electronics'})
    
    # GET request - show contact form
    context = {
        'title': 'Contact Us - Saylo Electronics',
    }
    return render(request, 'shop/contact.html', context)