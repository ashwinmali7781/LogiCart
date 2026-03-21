import json
import logging
from math import ceil

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Product, Contact, Orders, OrderUpdate, Review, Wishlist, Coupon, Newsletter, ReturnRequest
from shop.payTm import Checksum

logger = logging.getLogger(__name__)

MERCHANT_KEY = 'Your-Merchant-Key-Here'
MERCHANT_ID = 'Your-Merchant-Id-Here'
_PAYTM_CONFIGURED = (
    len(MERCHANT_KEY) == 32
    and MERCHANT_KEY != 'Your-Merchant-Key-Here'
    and MERCHANT_ID != 'Your-Merchant-Id-Here'
)


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def _send_order_email(order, subject, template_name):
    """Send an HTML email to the customer for order events."""
    try:
        html_message = render_to_string(template_name, {'order': order})
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception:
        logger.exception('Failed to send order email for order #%s', order.order_id)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_allprods(queryset):
    allProds = []
    cats = queryset.values_list('category', flat=True).distinct()
    for cat in cats:
        prod = list(queryset.filter(category=cat))
        n = len(prod)
        nSlides = ceil(n / 4)
        allProds.append([prod, range(1, nSlides), nSlides])
    return allProds


def _search_match(query, item):
    q = query.lower()
    return (q in item.product_name.lower() or q in item.desc.lower() or q in item.category.lower())


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# ── Public views ──────────────────────────────────────────────────────────────

def index(request):
    active_prods = Product.objects.filter(is_active=True)
    allProds = _build_allprods(active_prods)
    featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
    return render(request, 'shop/index.html', {'allProds': allProds, 'featured': featured})


@require_GET
def search(request):
    query = request.GET.get('search', '').strip()
    cat_filter = request.GET.get('cat', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    sort_by = request.GET.get('sort', '').strip()
    page_num = request.GET.get('page', 1)

    qs = Product.objects.filter(is_active=True)

    # Text search
    if query:
        if len(query) < 2:
            messages.warning(request, 'Please enter at least 2 characters to search.')
            return redirect('ShopHome')
        qs = [p for p in qs if _search_match(query, p)]
        qs = Product.objects.filter(id__in=[p.id for p in qs], is_active=True)

    # Category filter
    if cat_filter:
        qs = qs.filter(category=cat_filter)

    # Price range filter
    try:
        if min_price:
            qs = qs.filter(price__gte=int(min_price))
        if max_price:
            qs = qs.filter(price__lte=int(max_price))
    except ValueError:
        pass

    # Sort
    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-pub_date',
        'name': 'product_name',
    }
    qs = qs.order_by(sort_map.get(sort_by, '-pub_date'))

    # Filter by minimum rating (in Python since avg_rating is a property)
    if min_rating:
        try:
            min_r = float(min_rating)
            qs = [p for p in qs if p.avg_rating >= min_r]
        except ValueError:
            pass

    # Paginate — 12 products per page
    paginator = Paginator(list(qs) if not isinstance(qs, list) else qs, 12)
    page_obj = paginator.get_page(page_num)

    # All categories for filter dropdown
    all_categories = Product.objects.filter(is_active=True).values_list('category', flat=True).distinct()

    if not page_obj.object_list:
        messages.info(request, f'No products matched your filters.')

    return render(request, 'shop/search.html', {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,
        'cat_filter': cat_filter,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'sort_by': sort_by,
        'all_categories': all_categories,
    })


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        desc = request.POST.get('desc', '').strip()

        if not name or not email or not desc:
            messages.error(request, 'Name, email, and message are required.')
            return render(request, 'shop/contact.html')

        Contact(name=name, email=email, phone=phone, desc=desc).save()
        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        return redirect('ContactUs')

    return render(request, 'shop/contact.html')


def tracker(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderId', '').strip()
        email = request.POST.get('email', '').strip()

        if not order_id or not email:
            return JsonResponse({'status': 'error', 'message': 'Order ID and email are required.'})

        try:
            order = Orders.objects.filter(order_id=order_id, email=email).first()
            if not order:
                return JsonResponse({'status': 'noitem'})

            updates = list(order.updates.values('update_desc', 'timestamp'))
            serialized = [{'text': u['update_desc'], 'time': str(u['timestamp'])} for u in updates]
            return JsonResponse({
                'status': 'success',
                'updates': serialized,
                'itemsJson': order.items_json,
                'order_status': order.get_status_display(),
            })
        except Exception:
            logger.exception('Error in tracker for order_id=%s', order_id)
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'})

    return render(request, 'shop/tracker.html')


def productView(request, myid):
    product = get_object_or_404(Product, id=myid, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=myid)[:4]
    reviews = product.reviews.filter(is_approved=True)
    session_key = _get_session_key(request)
    in_wishlist = Wishlist.objects.filter(session_key=session_key, product=product).exists()

    # Recently viewed — store up to 10 product IDs in session
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if myid in recently_viewed_ids:
        recently_viewed_ids.remove(myid)
    recently_viewed_ids.insert(0, myid)
    request.session['recently_viewed'] = recently_viewed_ids[:10]

    # Fetch recently viewed products (excluding current)
    rv_ids = recently_viewed_ids[1:7]
    recently_viewed = []
    if rv_ids:
        rv_map = {p.id: p for p in Product.objects.filter(id__in=rv_ids, is_active=True)}
        recently_viewed = [rv_map[i] for i in rv_ids if i in rv_map]

    if request.method == 'POST' and request.POST.get('action') == 'review':
        r_name = request.POST.get('r_name', '').strip()
        r_email = request.POST.get('r_email', '').strip()
        r_rating = request.POST.get('r_rating', '0')
        r_comment = request.POST.get('r_comment', '').strip()
        try:
            rating_int = int(r_rating)
            if not r_name or not r_email or not r_comment or not (1 <= rating_int <= 5):
                raise ValueError
            Review.objects.create(
                product=product, name=r_name, email=r_email,
                rating=rating_int, comment=r_comment
            )
            messages.success(request, 'Thanks! Your review has been submitted for approval.')
        except (ValueError, TypeError):
            messages.error(request, 'Please fill in all review fields with a valid rating (1-5).')
        return redirect('ProductView', myid=myid)

    return render(request, 'shop/prodView.html', {
        'product': product,
        'related': related,
        'reviews': reviews,
        'in_wishlist': in_wishlist,
        'recently_viewed': recently_viewed,
    })


def checkout(request):
    if request.method == 'POST':
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '').strip()
        amount = request.POST.get('amount', '0').strip()
        email = request.POST.get('email', '').strip()
        address = (request.POST.get('address1', '').strip() + ' ' + request.POST.get('address2', '').strip()).strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        phone = request.POST.get('phone', '').strip()
        coupon_code = request.POST.get('coupon_code', '').strip().upper()

        if not all([name, email, address, city, state, zip_code, phone, items_json]):
            messages.error(request, 'All fields are required. Please complete the form.')
            return render(request, 'shop/checkout.html')

        try:
            amount_int = int(amount)
        except ValueError:
            messages.error(request, 'Invalid amount.')
            return render(request, 'shop/checkout.html')

        # Apply coupon
        coupon_obj = None
        discount_amount = 0
        if coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code=coupon_code)
                if coupon_obj.is_valid(amount_int):
                    final_amount = coupon_obj.apply(amount_int)
                    discount_amount = amount_int - final_amount
                    amount_int = final_amount
                    coupon_obj.used_count += 1
                    coupon_obj.save()
                else:
                    messages.warning(request, 'Coupon is invalid or expired.')
                    coupon_obj = None
            except Coupon.DoesNotExist:
                messages.warning(request, 'Coupon code not found.')

        order = Orders(
            items_json=items_json, name=name, email=email,
            address=address, city=city, state=state,
            zip_code=zip_code, phone=phone, amount=amount_int,
            discount_amount=discount_amount, coupon=coupon_obj,
        )
        order.save()
        OrderUpdate(order=order, update_desc='The order has been placed').save()
        # Send confirmation email
        _send_order_email(order, f'Order Confirmed – #{order.order_id} | LogiCart', 'shop/emails/order_confirmed.html')

        if _PAYTM_CONFIGURED:
            param_dict = {
                'MID': MERCHANT_ID,
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount_int),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',
            }
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return render(request, 'shop/paytm.html', {'param_dict': param_dict})
        else:
            return render(request, 'shop/order_confirmed.html', {'order': order})

    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = dict(form.items())
    checksum = response_dict.pop('CHECKSUMHASH', '')
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict.get('RESPCODE') == '01':
            logger.info('Payment successful for order %s', response_dict.get('ORDERID'))
        else:
            logger.warning('Payment failed for order %s: %s', response_dict.get('ORDERID'), response_dict.get('RESPMSG', ''))
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})


# ── Wishlist ──────────────────────────────────────────────────────────────────

def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    session_key = _get_session_key(request)
    obj, created = Wishlist.objects.get_or_create(session_key=session_key, product=product)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed', 'message': f'{product.product_name} removed from wishlist.'})
    return JsonResponse({'status': 'added', 'message': f'{product.product_name} added to wishlist!'})


def wishlist_view(request):
    session_key = _get_session_key(request)
    items = Wishlist.objects.filter(session_key=session_key).select_related('product')
    return render(request, 'shop/wishlist.html', {'items': items})


# ── Coupon API ────────────────────────────────────────────────────────────────

def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        amount = int(request.POST.get('amount', 0))
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid(amount):
                final = coupon.apply(amount)
                return JsonResponse({
                    'status': 'ok',
                    'discount': amount - final,
                    'final_amount': final,
                    'message': f'Coupon applied! You save Rs. {amount - final}',
                })
            return JsonResponse({'status': 'invalid', 'message': 'Coupon invalid, expired, or minimum order not met.'})
        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'notfound', 'message': 'Coupon code not found.'})
    return JsonResponse({'status': 'error'}, status=405)


# ── Product Comparison ────────────────────────────────────────────────────────

def compare_products(request):
    ids_raw = request.GET.get('ids', '')
    ids = []
    for part in ids_raw.split(','):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    ids = ids[:3]  # Max 3 products
    products = list(Product.objects.filter(id__in=ids, is_active=True))
    # Preserve order
    id_to_prod = {p.id: p for p in products}
    products = [id_to_prod[i] for i in ids if i in id_to_prod]
    return render(request, 'shop/compare.html', {'products': products})


# ── Returns & Refunds ─────────────────────────────────────────────────────────

def request_return(request):
    """Customer submits a return request by providing order ID + email."""
    order = None
    existing_request = None

    if request.method == 'POST':
        order_id = request.POST.get('order_id', '').strip()
        email = request.POST.get('email', '').strip()
        reason = request.POST.get('reason', '').strip()
        description = request.POST.get('description', '').strip()

        # Look up order
        try:
            order = Orders.objects.get(order_id=order_id, email=email)
        except Orders.DoesNotExist:
            messages.error(request, 'No order found with that ID and email.')
            return render(request, 'shop/return_request.html', {'reason_choices': ReturnRequest.REASON_CHOICES})

        # Only allow returns on delivered orders
        if order.status != 'delivered':
            messages.warning(request, f'Returns can only be requested for delivered orders. Your order status is: {order.get_status_display()}.')
            return render(request, 'shop/return_request.html', {'order': order, 'reason_choices': ReturnRequest.REASON_CHOICES})

        # Check if already requested
        existing_request = ReturnRequest.objects.filter(order=order).first()
        if existing_request:
            messages.info(request, f'A return request already exists for this order (status: {existing_request.get_status_display()}).')
            return render(request, 'shop/return_request.html', {
                'order': order,
                'existing_request': existing_request,
                'reason_choices': ReturnRequest.REASON_CHOICES,
            })

        if reason and description:
            ReturnRequest.objects.create(order=order, reason=reason, description=description)
            messages.success(request, 'Your return request has been submitted. We will review it within 2-3 business days.')
            return redirect('ReturnRequest')

    return render(request, 'shop/return_request.html', {'reason_choices': ReturnRequest.REASON_CHOICES})


# ── Newsletter ────────────────────────────────────────────────────────────────

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            _, created = Newsletter.objects.get_or_create(email=email)
            if created:
                return JsonResponse({'status': 'ok', 'message': 'Subscribed! Thanks for joining.'})
            return JsonResponse({'status': 'exists', 'message': 'You are already subscribed.'})
    return JsonResponse({'status': 'error'}, status=400)
