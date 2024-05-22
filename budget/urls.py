from django.urls import path
from . import views
from .views import budget_delete
from .views import budget_graph
from .views import payment_delete
from django.contrib.auth import views as auth_views 


urlpatterns = [
    path('', views.user_login, name='user_login'),
    path('budget/new/', views.budget_create, name='budget_create'),
    path('budget/<int:budget_id>/make_payment/', views.make_payment, name='make_payment'),
    path('budget_edit/<int:id>/', views.budget_edit, name='budget_edit'),
    path('budget_delete/<int:id>/', budget_delete, name='budget_delete'),
    path('graph/', budget_graph, name="budget_graph"),
    path('main/', views.index, name='index' ),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('payment_edit/<int:id>/', views.payment_edit, name='payment_edit'),
    path('payment_delete/<int:id>/', payment_delete, name='payment_delete')
]
