from django import forms
from .models import Budget, Payment
import datetime


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'amount', 'description']

    date = forms.DateField(initial=datetime.date.today)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    description = forms.CharField()
    