# tienda/urls.py

from django.urls import path
from . import views # Importa las funciones de lógica (Vistas) que crearemos

urlpatterns = [
    # HOME / LANDING PAGE
    path('', views.index, name='inicio'), 
    
    # MENÚS Y CATÁLOGOS
    path('menu/', views.menu_virtual, name='menu_virtual'), 
    path('citricas/', views.frutas_citricas, name='frutas_citricas'), 
    path('dulces/', views.frutas_dulces, name='frutas_dulces'),
    path('neutras/', views.frutas_neutras, name='frutas_neutras'),
    path('ofertas/', views.ver_ofertas, name='ver_ofertas'),
    
    # AUTENTICACIÓN
    path('registro/', views.registro_usuario, name='registro'),
    path('iniciar-sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),

    path('compra/', views.confirmar_compra, name='compra'),
    
    # CARRITO Y COMPRA
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('comprar/', views.confirmar_compra, name='confirmar_compra'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar-carrito/<int:producto_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('ajustar-cantidad/<int:producto_id>/<str:accion>/', views.ajustar_cantidad, name='ajustar_cantidad'),
    
    # ACCIONES (Estas no muestran páginas completas, solo procesan datos)
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),

    path('orden-confirmada/<int:pedido_id>/', views.orden_confirmada, name='orden_confirmada'),
]