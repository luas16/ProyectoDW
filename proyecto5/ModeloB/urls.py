from django.urls import path
from ModeloB.views.categoria.views import *
from ModeloB.views.clientes.views import *
from ModeloB.views.principal.views import *
from ModeloB.views.product.views import *
from ModeloB.views.ventas.views import *

urlpatterns = [
    #path('category/index/', category_list),
    path('category/list/', CategoriaListView.as_view(), name='categoria'),
    path('category/add/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('category/edit/<int:pk>/', CategariaUpdateView.as_view(), name='categoria_update'),
    path('category/delete/<int:pk>/', CaregoriaDeleteView.as_view(), name='categoria_delete'),
    #principal
    path('principal/', PrincipalView.as_view(), name= 'home'),
    path('compras/', ComprasView.as_view(), name= 'compras'),

    #Clientes
    path('clientes/list/', ClientesListView.as_view(), name='clientes'),
    path('clientes/add/', ClientesCreateView.as_view(), name='cliente_create'),
    path('clientes/edit/<int:pk>/', ClientesUpdateView.as_view(), name='cliente_update'),
    path('clientes/delete/<int:pk>/', ClientesDeleteView.as_view(), name='cliente_delete'),

    #productos
    path('productos/list/', ProductosListView.as_view(), name='productos'),
    path('productos/add/', ProductosCreateView.as_view(), name='producto_create'),
    path('productos/edit/<int:pk>/', ProductosUpdateView.as_view(), name='producto_update'),
    path('productos/delete/<int:pk>/', ProductosDeleteView.as_view(), name='producto_delete'),

    #ventas
    path('ventas/list/', VentasListView.as_view(), name='ventas'),
    path('ventas/add/', VentasCreateView.as_view(), name='ventas_create'),
    path('ventas/delete/<int:pk>/', VentasDeleteView.as_view(), name='ventas_delete'),
    path('ventas/edit/<int:pk>/', VentasUpdateView.as_view(), name='ventas_update'),
    path('ventas/factura/pdf/<int:pk>/', facturaPDFView.as_view(), name='ventas_factura'),

]