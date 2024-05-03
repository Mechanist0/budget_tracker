from django.shortcuts import render, redirect
from .models import Budget, Payment
from .forms import BudgetForm, PaymentForm
from django.db.models import Sum
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import SignUpForm


def index(request):
    """View function for home page of site."""
    budgets = Budget.objects.filter(user=request.user).prefetch_related('payments')
    for budget in budgets:
        total_payments = budget.payments.aggregate(total=Sum('amount'))['total'] or 0
        budget.remaining_balance = budget.amount - total_payments
    return render(request, 'index.html', {'budgets': budgets})

def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user 
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
    return render(request, 'make_payment.html', {'budget': budget, 'form': form})

def budget_edit(request, id):
    try:
        budget = Budget.objects.get(id=id, user=request.user)
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

def budget_delete(request, id):
    try:
        budget = Budget.objects.get(id=id, user=request.user)
    except Budget.DoesNotExist:
        return redirect('index')
    
    if request.method == 'POST':
        budget.delete()
        return redirect('index')  
    

#Graph starts here


def budget_graph(request):
    data = Budget.objects.filter(user=request.user)
    context = { 'data' : data, }
    
    return render(request, 'budget_graph.html', context)


#Graph ends here

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