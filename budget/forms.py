from django import forms
from .models import Category, Payment
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category', 'amount']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'amount', 'description']

    date = forms.DateField(initial=datetime.date.today)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    description = forms.CharField()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    username = forms.CharField(help_text='', required=True)
    password1 = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput, help_text='',)
    password2 = forms.CharField(label="Password confimation", strip=False, widget=forms.PasswordInput, help_text="Reenter the password.")
    

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    

