from django.urls import path
from . import views
from .views import budget_delete
from .views import budget_graph

urlpatterns = [
    path('', views.index, name='index'),
    path('budget/new/', views.budget_create, name='budget_create'),
    path('budget/<int:budget_id>/make_payment/', views.make_payment, name='make_payment'),
    path('budget_edit/<int:id>/', views.budget_edit, name='budget_edit'),
    path('budget_delete/<int:id>/', budget_delete, name='budget_delete'),
    path('graph/', budget_graph, name="budget_graph")
]
