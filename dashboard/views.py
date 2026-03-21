import json
from datetime import timedelta, date
from collections import defaultdict

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, Q
from django.views.decorators.http import require_POST
import csv

from shop.models import Product, Orders, OrderUpdate, Contact, Review, Coupon, Newsletter, Wishlist, ReturnRequest


# ── Access guard ──────────────────────────────────────────────────────────────
def admin_required(view_func):
    return staff_member_required(view_func, login_url='/admin/login/')


# ── Dashboard Home ────────────────────────────────────────────────────────────
@admin_required
def dashboard_home(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    total_orders = Orders.objects.count()
    total_revenue = Orders.objects.exclude(status='cancelled').aggregate(s=Sum('amount'))['s'] or 0
    total_products = Product.objects.filter(is_active=True).count()
    total_customers = Orders.objects.values('email').distinct().count()
    unread_messages = Contact.objects.filter(is_read=False).count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    low_stock = Product.objects.filter(stock__lte=5, is_active=True).count()
    pending_returns = ReturnRequest.objects.filter(status='pending').count()

    # Orders last 30 days for chart
    orders_by_day = {}
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        orders_by_day[d.strftime('%d %b')] = 0
    recent_orders_qs = Orders.objects.filter(created_at__date__gte=thirty_days_ago)
    for order in recent_orders_qs:
        key = order.created_at.date().strftime('%d %b')
        if key in orders_by_day:
            orders_by_day[key] += 1

    # Revenue last 7 days
    revenue_by_day = {}
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        revenue_by_day[d.strftime('%d %b')] = 0
    for order in Orders.objects.filter(created_at__date__gte=seven_days_ago).exclude(status='cancelled'):
        key = order.created_at.date().strftime('%d %b')
        if key in revenue_by_day:
            revenue_by_day[key] += order.amount

    # Orders by status
    status_counts = dict(Orders.objects.values_list('status').annotate(c=Count('status')))

    # Top products by orders
    top_products = (
        Product.objects.filter(is_active=True)
        .annotate(wishlist_count=Count('wishlisted_by'))
        .order_by('-wishlist_count')[:5]
    )

    # Recent orders
    recent_orders = Orders.objects.select_related('coupon').order_by('-created_at')[:10]

    ctx = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_customers': total_customers,
        'unread_messages': unread_messages,
        'pending_reviews': pending_reviews,
        'pending_returns': pending_returns,
        'low_stock': low_stock,
        'orders_chart_labels': json.dumps(list(orders_by_day.keys())),
        'orders_chart_data': json.dumps(list(orders_by_day.values())),
        'revenue_chart_labels': json.dumps(list(revenue_by_day.keys())),
        'revenue_chart_data': json.dumps(list(revenue_by_day.values())),
        'status_labels': json.dumps(list(status_counts.keys())),
        'status_data': json.dumps(list(status_counts.values())),
        'top_products': top_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/home.html', ctx)


# ── Products ──────────────────────────────────────────────────────────────────
@admin_required
def product_list(request):
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('cat', '')
    prods = Product.objects.all()
    if q:
        prods = prods.filter(Q(product_name__icontains=q) | Q(category__icontains=q))
    if cat:
        prods = prods.filter(category=cat)
    categories = Product.objects.values_list('category', flat=True).distinct()
    return render(request, 'dashboard/products.html', {'products': prods, 'categories': categories, 'q': q, 'sel_cat': cat})


@admin_required
def product_add(request):
    if request.method == 'POST':
        try:
            p = Product(
                product_name=request.POST['product_name'],
                category=request.POST['category'],
                subcategory=request.POST.get('subcategory', ''),
                price=int(request.POST['price']),
                original_price=int(request.POST.get('original_price') or 0),
                stock=int(request.POST.get('stock', 0)),
                desc=request.POST.get('desc', ''),
                pub_date=request.POST['pub_date'],
                is_featured=bool(request.POST.get('is_featured')),
                is_active=bool(request.POST.get('is_active', True)),
            )
            if 'image' in request.FILES:
                p.image = request.FILES['image']
            p.save()
            messages.success(request, f'Product "{p.product_name}" added successfully.')
            return redirect('dashboard_products')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    from django.utils.timezone import now
    return render(request, 'dashboard/product_form.html', {'action': 'Add', 'today': now().date()})


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product.product_name = request.POST['product_name']
            product.category = request.POST['category']
            product.subcategory = request.POST.get('subcategory', '')
            product.price = int(request.POST['price'])
            product.original_price = int(request.POST.get('original_price') or 0)
            product.stock = int(request.POST.get('stock', 0))
            product.desc = request.POST.get('desc', '')
            product.pub_date = request.POST['pub_date']
            product.is_featured = bool(request.POST.get('is_featured'))
            product.is_active = bool(request.POST.get('is_active'))
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.save()
            messages.success(request, f'Product "{product.product_name}" updated.')
            return redirect('dashboard_products')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'dashboard/product_form.html', {'action': 'Edit', 'product': product})


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.product_name
        product.is_active = False  # Soft delete
        product.save()
        messages.success(request, f'Product "{name}" deactivated.')
    return redirect('dashboard_products')


# ── Orders ────────────────────────────────────────────────────────────────────
@admin_required
def order_list(request):
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    orders = Orders.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    if q:
        orders = orders.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(order_id__icontains=q))
    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'status_choices': Orders.STATUS_CHOICES,
        'sel_status': status_filter,
        'q': q,
    })


@admin_required
def order_detail(request, pk):
    order = get_object_or_404(Orders, pk=pk)
    updates = order.updates.all()
    try:
        items = json.loads(order.items_json)
    except Exception:
        items = {}

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Orders.STATUS_CHOICES):
                order.status = new_status
                order.save()
                desc = f'Status updated to: {order.get_status_display()}'
                OrderUpdate.objects.create(order=order, update_desc=desc)
                messages.success(request, 'Order status updated.')
                # Send status update email
                try:
                    from django.core.mail import send_mail
                    from django.template.loader import render_to_string
                    from django.conf import settings
                    html = render_to_string('shop/emails/order_status_update.html', {'order': order})
                    send_mail(
                        subject=f'Your Order #{order.order_id} is now {order.get_status_display()} – LogiCart',
                        message='',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email],
                        html_message=html,
                        fail_silently=True,
                    )
                except Exception:
                    pass
        elif action == 'add_note':
            note = request.POST.get('note', '').strip()
            if note:
                OrderUpdate.objects.create(order=order, update_desc=note)
                messages.success(request, 'Note added.')
        return redirect('dashboard_order_detail', pk=pk)

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'updates': updates,
        'items': items,
        'status_choices': Orders.STATUS_CHOICES,
    })


@admin_required
def orders_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Name', 'Email', 'Phone', 'Amount', 'Status', 'City', 'State', 'Created At'])
    for o in Orders.objects.all():
        writer.writerow([o.order_id, o.name, o.email, o.phone, o.amount, o.get_status_display(), o.city, o.state, o.created_at.strftime('%Y-%m-%d %H:%M')])
    return response


# ── Reviews ───────────────────────────────────────────────────────────────────
@admin_required
def review_list(request):
    filter_q = request.GET.get('filter', 'pending')
    reviews = Review.objects.select_related('product')
    if filter_q == 'pending':
        reviews = reviews.filter(is_approved=False)
    elif filter_q == 'approved':
        reviews = reviews.filter(is_approved=True)
    return render(request, 'dashboard/reviews.html', {'reviews': reviews, 'filter': filter_q})


@admin_required
@require_POST
def review_action(request, pk):
    review = get_object_or_404(Review, pk=pk)
    action = request.POST.get('action')
    if action == 'approve':
        review.is_approved = True
        review.save()
        messages.success(request, 'Review approved.')
    elif action == 'delete':
        review.delete()
        messages.success(request, 'Review deleted.')
    return redirect('dashboard_reviews')


# ── Messages ──────────────────────────────────────────────────────────────────
@admin_required
def message_list(request):
    filter_q = request.GET.get('filter', 'unread')
    msgs = Contact.objects.all()
    if filter_q == 'unread':
        msgs = msgs.filter(is_read=False)
    return render(request, 'dashboard/messages.html', {'msgs': msgs, 'filter': filter_q})


@admin_required
def message_detail(request, pk):
    msg = get_object_or_404(Contact, pk=pk)
    msg.is_read = True
    msg.save()
    return render(request, 'dashboard/message_detail.html', {'msg': msg})


# ── Coupons ───────────────────────────────────────────────────────────────────
@admin_required
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'dashboard/coupons.html', {'coupons': coupons})


@admin_required
def coupon_add(request):
    if request.method == 'POST':
        try:
            Coupon.objects.create(
                code=request.POST['code'].upper(),
                discount_type=request.POST['discount_type'],
                discount_value=int(request.POST['discount_value']),
                min_order_amount=int(request.POST.get('min_order_amount', 0)),
                max_uses=int(request.POST.get('max_uses', 100)),
                valid_from=request.POST['valid_from'],
                valid_to=request.POST['valid_to'],
            )
            messages.success(request, 'Coupon created.')
            return redirect('dashboard_coupons')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'dashboard/coupon_form.html', {'action': 'Add', 'today': date.today()})


@admin_required
def coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted.')
    return redirect('dashboard_coupons')


# ── Return Requests ────────────────────────────────────────────────────────────
@admin_required
def return_list(request):
    status_filter = request.GET.get('status', '')
    returns = ReturnRequest.objects.select_related('order')
    if status_filter:
        returns = returns.filter(status=status_filter)
    return render(request, 'dashboard/returns.html', {
        'returns': returns,
        'status_choices': ReturnRequest.STATUS_CHOICES,
        'sel_status': status_filter,
    })


@admin_required
@require_POST
def return_action(request, pk):
    ret = get_object_or_404(ReturnRequest, pk=pk)
    action = request.POST.get('action')
    note = request.POST.get('admin_note', '').strip()
    status_map = {'approve': 'approved', 'reject': 'rejected', 'complete': 'completed'}
    if action in status_map:
        ret.status = status_map[action]
        if note:
            ret.admin_note = note
        ret.save()
        messages.success(request, f'Return request #{pk} marked as {ret.get_status_display()}.')
    return redirect('dashboard_returns')


# ── Newsletter ────────────────────────────────────────────────────────────────
@admin_required
def newsletter_list(request):
    subscribers = Newsletter.objects.filter(is_active=True)
    return render(request, 'dashboard/newsletter.html', {'subscribers': subscribers})


@admin_required
def newsletter_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
    writer = csv.writer(response)
    writer.writerow(['Email', 'Subscribed At'])
    for s in Newsletter.objects.filter(is_active=True):
        writer.writerow([s.email, s.subscribed_at.strftime('%Y-%m-%d')])
    return response
