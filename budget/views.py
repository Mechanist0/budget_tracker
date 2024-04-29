from django.shortcuts import render, redirect
from .models import Budget, Payment
from .forms import BudgetForm, PaymentForm
from django.db.models import Sum


def index(request):
    """View function for home page of site."""
    budgets = Budget.objects.all().prefetch_related('payments')
    for budget in budgets:
        total_payments = budget.payments.aggregate(total=Sum('amount'))['total'] or 0
        budget.remaining_balance = budget.amount - total_payments
    return render(request, 'index.html', {'budgets': budgets})

def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BudgetForm()
    return render(request, 'budget_create.html', {'form': form})

def make_payment(request, budget_id):
    budget = Budget.objects.get(pk=budget_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Extract form data
            date = form.cleaned_data['date']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            # Create and save Payment instance
            payment = Payment(date=date, amount=amount, description=description, budget=budget)
            payment.save()

            return redirect('index')  # Redirect to budget list after payment
    else:
        form = PaymentForm()
    return render(request, 'make_payment.html', {'budget': budget, 'form': form})

def budget_edit(request, id):
    try:
        budget = Budget.objects.get(id=id)
    except Budget.DoesNotExist:
        raise Http404("Budget does not exist")

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BudgetForm(instance=budget)
    
    return render(request, 'budget_edit.html', {'form': form})
