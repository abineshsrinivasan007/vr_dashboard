from django.shortcuts import render
from .models import Plan

def subscription_plans(request):
    plans = Plan.objects.all()  # fetch all plans from DB
    return render(request, 'subscription/plans.html', {'plans': plans})


from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from .models import Plan, Subscription
from django.utils import timezone

def subscribe(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        college_name = request.POST['college_name']
        email = request.POST['email']
        phone = request.POST['phone']

        # Create subscription (not paid yet)
        subscription = Subscription.objects.create(
            plan=plan,
            college_name=college_name,
            email=email,
            phone=phone,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=plan.duration*30)
        )

        # Redirect to payment page
        return redirect('subscription:payment', sub_id=subscription.id)

# 2️⃣ Payment page (dummy/test mode)
def payment(request, sub_id):
    subscription = get_object_or_404(Subscription, id=sub_id)
    if request.method == 'POST':
        # Simulate payment success
        subscription.payment_done = True
        subscription.save()

        # Send success email
        send_mail(
            subject='Subscription Successful',
            message=f'Hi {subscription.college_name}, your subscription to {subscription.plan.name} is successful!',
            from_email='no-reply@yourdomain.com',
            recipient_list=[subscription.email],
            fail_silently=False,
        )
        return redirect('subscription:success', sub_id=subscription.id)

    return render(request, 'subscription/payment.html', {'subscription': subscription})

# 3️⃣ Success page
def success(request, sub_id):
    subscription = get_object_or_404(Subscription, id=sub_id)
    return render(request, 'subscription/success.html', {'subscription': subscription})
