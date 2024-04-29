from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('budget/new/', views.budget_create, name='budget_create'),
    path('budget/<int:budget_id>/make_payment/', views.make_payment, name='make_payment'),
]
