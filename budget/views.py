from datetime import timedelta, datetime

from django.db.models.functions import Cast
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Category, Payment, TimePeriod, CurrentTimePeriod
from .forms import BudgetForm, PaymentForm, CurrentPeriodForm
from django.db.models import Sum, ExpressionWrapper, BooleanField, Q, Case, When, F, IntegerField, Value, QuerySet
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import SignUpForm


def index(request):
    """View function for home page of site."""
    budgets = Category.objects.filter(user=request.user, timeperiod__in=get_period_tree()).prefetch_related(
        'payments')
    total_balance = 0
    for budget in budgets:
        total_payments = budget.payments.aggregate(total=Sum('amount'))['total'] or 0
        budget.remaining_balance = budget.amount - total_payments
        total_balance += budget.remaining_balance
    balance = get_balance(request.user)
    return render(request, 'index.html',
                  {'budgets': budgets, 'balance': balance, 'period': get_current_time_period().id})


def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.timeperiod = TimePeriod.objects.filter(user=request.user).order_by('-index').first()
            budget.save()
            return redirect('index')
    else:
        form = BudgetForm()
    return render(request, 'budget_create.html',
                  {'form': form, 'balance': get_balance(request.user), 'period': get_current_time_period().id})


def make_payment(request, budget_id):
    budget = Category.objects.get(pk=budget_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Extract form data
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            # Create and save Payment instance
            payment = Payment.objects.create(
                user=request.user,
                budget=budget,
                date=date,
                amount=amount,
                description=description
            )

            return redirect('index')  # Redirect to budget list after payment
    else:
        form = PaymentForm()
    return render(request, 'make_payment.html', {'budget': budget, 'form': form, 'balance': get_balance(request.user),
                                                 'period': get_current_time_period().id})


def payment_edit(request, id):
    try:
        payment = Payment.objects.get(id=id)
    except Payment.DoesNotExist:
        raise Http404("Payment does not exist")

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Update the payment object with form data
            payment.date = form.cleaned_data['date']
            payment.amount = form.cleaned_data['amount']
            payment.description = form.cleaned_data['description']
            payment.save()
            return redirect('index')
    else:
        # Populate the form with payment data
        form = PaymentForm(initial={
            'date': payment.date,
            'amount': payment.amount,
            'description': payment.description
        })

    return render(request, 'payment_edit.html', {'form': form, 'period': get_current_time_period().id})


def payment_delete(request, id):
    try:
        payment = Payment.objects.get(id=id)
    except Payment.DoesNotExist:
        raise Http404("payment does not exist")

    if request.method == 'POST':
        payment.delete()
        return redirect("index")


def budget_edit(request, id):
    try:
        budget = Category.objects.get(id=id, user=request.user)
        budget.user = request.user
    except Category.DoesNotExist:
        raise Http404("Budget does not exist")

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'budget_edit.html',
                  {'form': form, 'balance': get_balance(request.user), 'period': get_current_time_period().id})


def budget_delete(request, id):
    try:
        budget = Category.objects.get(id=id, user=request.user)
    except Category.DoesNotExist:
        return redirect('index')

    if request.method == 'POST':
        budget.delete()
        return redirect('index')


# Graph starts here
def budget_graph(request):
    data = Category.objects.filter(user=request.user)
    balance = get_balance(request.user)
    context = {'data': data, 'balance': balance, 'period': get_current_time_period().id}
    return render(request, 'budget_graph.html', context)


# Graph ends here


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirect to dashboard or any other page
    else:
        form = AuthenticationForm()
    return render(request, 'user_login.html', {'form': form})


def current_time_period_edit(request, id):
    try:
        period = CurrentTimePeriod.objects.get(id=id, user=request.user)
    except Category.DoesNotExist:
        raise Http404("Period does not exist")

    if request.method == 'POST':
        form = CurrentPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CurrentPeriodForm(instance=period)

    return render(request, 'current_time_period_edit.html',
                  {'form': form, 'balance': get_balance(request.user), 'period': get_current_time_period().id})


def logout_view(request):
    logout(request)
    return redirect('user_login')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')  # Redirect to login page after successful signup
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def get_balance(user):
    budgets = Category.objects.filter(user=user).prefetch_related('payments')
    total = 0
    for budget in budgets:
        total_payments = budget.payments.aggregate(total=Sum('amount'))['total'] or 0
        total += budget.amount - total_payments
    return total


def get_current_time_period():
    return CurrentTimePeriod.objects.first()


def get_period_tree():
    current_period = get_current_time_period()

    queryset = TimePeriod.objects.get_queryset()
    return_set = []
    for q in queryset:
        if q.is_in_timeperiod(current_period):
            return_set.append(q)

    # Filter and count the items that are in the current period
    return return_set