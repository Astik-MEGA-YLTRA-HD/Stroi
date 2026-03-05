from django.urls import path
from program.views import (
    CustomLoginView, logout_view, register_view,
    index, add_order, day, add_day, consumables,
    add_consumables, add_payment, edit_consumables, edit_payment, document
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),  # новая функция
    path('register/', register_view, name='register'),
    path('', index, name='index'),
    path('order/add/', add_order, name='add_order'),
    path('order/<int:_id>/day/', day, name='day'),
    path('order/<int:_id>/day/add/', add_day, name='add_day'),
    path('day/<int:_id>/consumables/', consumables, name='consumables'),
    path('day/<int:_id>/consumables/add/', add_consumables, name='add_consumables'),
    path('day/<int:_id>/payment/add/', add_payment, name='add_payment'),
    path('consumables/<int:_id>/edit/', edit_consumables, name='edit_consumables'),
    path('payment/<int:_id>/edit/', edit_payment, name='edit_payment'),
    path('day/<int:_id>/document/', document, name='document'),
]