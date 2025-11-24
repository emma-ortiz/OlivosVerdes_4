# tienda/admin.py

from django.contrib import admin
from .models import Sucursal, Categoria, Producto, Oferta, PerfilCliente, Compra, DetalleCompra

# Registra todos tus modelos para que aparezcan en el panel de administración
admin.site.register(Sucursal)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Oferta)

# Opcional: Para el PerfilCliente, lo registras junto al modelo de Usuario
# admin.site.register(PerfilCliente) 

# Puedes registrar Compra y DetalleCompra con opciones de visualización más avanzadas,
# pero para empezar, un registro simple es suficiente.
admin.site.register(Compra)
admin.site.register(DetalleCompra)