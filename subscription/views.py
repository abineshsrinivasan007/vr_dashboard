from django.shortcuts import render
from .models import Plan

from django.shortcuts import render, get_object_or_404, redirect
from .models import Plan, Subscription
from django.utils import timezone
from django.core.mail import send_mail

def subscription_plans(request, plan_id=None, step=None):
    plans = Plan.objects.all()
    context = {'plans': plans}

    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)
        context['plan'] = plan

        if request.method == 'POST':
            if step == 'subscribe':  # First form submission
                college_name = request.POST['college_name']
                email = request.POST['email']
                password = request.POST['password']
                phone = request.POST['phone']

                subscription = Subscription.objects.create(
                    plan=plan,
                    college_name=college_name,
                    email=email,
                    password=password,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=30),
                )
                context['subscription'] = subscription
                context['step'] = 'payment'  # Next step
            elif step == 'payment':  # Payment form submission
                sub_id = request.POST['sub_id']
                subscription = get_object_or_404(Subscription, id=sub_id)
                subscription.active = True
                subscription.save()

                # Send confirmation email (optional)
                send_mail(
                    subject='Subscription Successful',
                    message=f'Hi {subscription.college_name}, your subscription to {subscription.plan.name} is active!',
                    from_email='no-reply@example.com',
                    recipient_list=[subscription.email],
                    fail_silently=True
                )

                context['subscription'] = subscription
                context['step'] = 'success'  # Show success message

        else:
            context['step'] = 'subscribe'  # Default to subscription form

    return render(request, 'subscription/plans.html', context)

from django.shortcuts import get_object_or_404, redirect
from .models import Plan, Subscription
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.mail import send_mail  # ✅ Add this line
from .models import Plan, Subscription


def subscribe(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        college_name = request.POST['college_name']
        email = request.POST['email']
        password = request.POST['password']

        # Create subscription (not paid yet)
        subscription = Subscription.objects.create(
            plan=plan,
            college_name=college_name,
            email=email,
            password=password,   # store hashed in production
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)  # 1 month for now
        )

        # Redirect to success page
        return redirect('subscription:success', sub_id=subscription.id)

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
