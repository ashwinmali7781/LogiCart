from shop.models import Contact, Review, ReturnRequest


def dashboard_context(request):
    """Inject unread counts into every dashboard template."""
    if not request.path.startswith('/dashboard/'):
        return {}
    if not request.user.is_staff:
        return {}
    return {
        'unread_messages': Contact.objects.filter(is_read=False).count(),
        'pending_reviews': Review.objects.filter(is_approved=False).count(),
        'pending_returns': ReturnRequest.objects.filter(status='pending').count(),
    }
