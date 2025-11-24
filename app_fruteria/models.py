from datetime import date
from django.db import models
from django.contrib.auth.models import User 

# ======================================================================
# 1. Sucursal
# ======================================================================
class Sucursal(models.Model):
    """Representa una ubicación física o un punto de distribución."""
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    
    def __str__(self):
        return self.nombre

# ======================================================================
# 2. Categoría (Cítricas, Dulces)
# ======================================================================
class Categoria(models.Model):
    """Representa una categoría de fruta (Cítricas o Dulces)."""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# ======================================================================
# 4. Oferta (Para descuentos dinámicos en ofertas.html)
# ======================================================================
class Oferta(models.Model):
    nombre = models.CharField(max_length=100, default='Oferta sin nombre')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name="¿Oferta Activa?")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    porcentaje_descuento = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=0,
    verbose_name="Porcentaje de Descuento (%)"
)
    # Puedes añadir campos como 'fecha_inicio', 'fecha_fin', 'porcentaje_descuento' si los necesitas.

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Ofertas"
# ======================================================================
# 3. Producto (Tus Frutas)
# ======================================================================
class Producto(models.Model):
    """Representa una fruta o verdura disponible en la tienda."""
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2) 
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True) 
    
    # Relaciones
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True) 
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, default=1) 
    oferta = models.ForeignKey(Oferta, on_delete=models.SET_NULL,  null=True,  blank=True, related_name='productos_en_oferta',verbose_name="Aplicar Oferta")
    @property
    def precio_final(self):
        """Calcula el precio del producto aplicando el descuento de la oferta vigente."""
        hoy = date.today()
        
        # 1. Verificar si hay una oferta asignada y si está vigente
        if self.oferta and self.oferta.fecha_inicio <= hoy <= self.oferta.fecha_fin:
            descuento_porcentaje = self.oferta.porcentaje_descuento
            
            # Cálculo: Precio original * (1 - Porcentaje / 100)
            descuento_monto = self.precio * (descuento_porcentaje / 100)
            precio_con_descuento = self.precio - descuento_monto
            
            # Devuelve el precio con descuento
            return precio_con_descuento
            
        # 2. Si no hay oferta vigente, devuelve el precio original
        return self.precio 

    def __str__(self):
        return self.nombre


# ======================================================================
# 5. Cliente (Perfil que complementa al User de Django)
# ======================================================================
class PerfilCliente(models.Model):
    """
    Extiende el modelo User de Django con campos adicionales.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=150, blank=True, null=True)
    correo = models.EmailField(max_length=254, blank=True, null=True)
    constaseña = models.CharField(max_length=128, blank=True, null=True)
    confirmar_contraseña = models.CharField(max_length=128, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f'Perfil de {self.user.username}'

# ======================================================================
# 6. Compra (El Encabezado de la Orden)
# ======================================================================
class Compra(models.Model):
    """Representa la orden de compra completa."""
    cliente = models.ForeignKey(User, on_delete=models.CASCADE) 
    fecha_compra = models.DateTimeField(auto_now_add=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.SET_NULL, null=True)
    total_compra = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=50, default='Pendiente') 

    def __str__(self):
        return f"Compra #{self.id} de {self.cliente.username}"

# ======================================================================
# 7. DetalleCompra (Los Productos dentro de la Orden)
# ======================================================================
class DetalleCompra(models.Model):
    """Representa un producto específico dentro de una Compra."""
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE) 
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) 
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2) 

    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
