from django.urls import path
from program import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_order/', views.add_order, name='add_order'),
    path('day/<int:_id>/', views.day, name='day'),
    path('add_day/<int:_id>/', views.add_day, name='add_day'),
    path('consumables/<int:_id>/', views.consumables, name='consumables'),
    path('add_consumables/<int:_id>/', views.add_consumables, name='add_consumables'),
    path('add_payment/<int:_id>/', views.add_payment, name='add_payment'),
    path('edit_consumables/<int:_id>/', views.edit_consumables, name='edit_consumables'),
    path('edit_payment/<int:_id>/', views.edit_payment, name='edit_payment'),
]