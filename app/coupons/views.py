from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CouponApplyForm
from .models import Coupon


@require_POST
def coupon_apply(request):
    """
    Applies a coupon code to the current session.

    This view handles the application of a coupon. It expects a POST request
    containing a coupon code. It validates the code against active and valid
    coupons in the database. If a valid coupon is found, its ID is stored
    in the user's session. Otherwise, any existing coupon ID in the session
    is removed.

    Args:
        request (HttpRequest): The HTTP request object. Expected to be a POST request.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page, regardless of
            whether a coupon was successfully applied or not.
    """
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data["code"]
        try:
            coupon = Coupon.objects.get(
                code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True,
            )
            request.session["coupon_id"] = coupon.id
        except Coupon.DoesNotExist:
            request.session["coupon_id"] = None
    return redirect("cart:cart_detail")
