# app_fruteria/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from django.contrib.auth.forms import AuthenticationForm
import datetime 
from decimal import Decimal # Importado una sola vez
from .forms import RegistroClienteForm
from django.http import JsonResponse
from django.db.models import Q 
from django.utils import timezone # Necesario para la fecha de compra
import decimal

# ====================================================================
# --- CORREGIDO: Importación de Modelos Limpia ---
# Importamos los modelos que SÍ existen en tu db.sqlite3
# Removemos 'Pedido' e 'ItemPedido' porque no existen.
# ====================================================================
from .models import (
    Producto, 
    Categoria, 
    Oferta, 
    PerfilCliente, 
    Sucursal,
    Compra,
    DetalleCompra
)

# --------------------------------------------------------------------------
# A. VISTAS DEL CATÁLOGO Y HOME
# --------------------------------------------------------------------------

def index(request):
    """
    Vista para la página principal (index.html).
    """
    productos_destacados = Producto.objects.all().order_by('-id')[:3] 
    
    contexto = {
        'productos_destacados': productos_destacados
    }
    return render(request, 'app_fruteria/index.html', contexto)

def menu_virtual(request):
    """
    Muestra el catálogo completo de productos (menu.html).
    """
    productos = Producto.objects.all().order_by('nombre')
    
    contexto = {
        'lista_productos': productos
    }
    return render(request, 'app_fruteria/menu.html', contexto)

def frutas_citricas(request):
    """
    Muestra solo las frutas de la categoría 'Cítricas' (citricas.html).
    """
    try:
        productos = Producto.objects.filter(categoria__nombre='Cítricas').order_by('nombre')
    except:
        productos = Producto.objects.none()

    contexto = {
        'lista_productos': productos,
        'nombre_seccion': 'Frutas Cítricas'
    }
    return render(request, 'app_fruteria/citricas.html', contexto)

def frutas_dulces(request):
    """
    Muestra solo las frutas de la categoría 'Dulces' (dulces.html).
    """
    try:
        productos = Producto.objects.filter(categoria__nombre='Dulces').order_by('nombre')
    except:
        productos = Producto.objects.none() 

    contexto = {
        'lista_productos': productos,
        'nombre_seccion': 'Frutas Dulces'
    }
    return render(request, 'app_fruteria/dulces.html', contexto)

def frutas_neutras(request):
    """
    Muestra solo las frutas de la categoría 'Neutras' (neutras.html).
    """
    try:
        productos = Producto.objects.filter(categoria__nombre='Neutras').order_by('nombre')
    except:
        productos = Producto.objects.none() 

    contexto = {
        'lista_productos': productos,
        'nombre_seccion': 'Frutas Neutras'
    }
    return render(request, 'app_fruteria/neutras.html', contexto)

def ver_ofertas(request):
    """
    Muestra todos los productos que están asignados a ofertas activas y vigentes.
    """
    hoy = datetime.date.today()
    
    
    lista_productos_oferta = Producto.objects.filter(
        oferta__isnull=False,
        oferta__fecha_inicio__lte=hoy, 
        oferta__fecha_fin__gte=hoy
    ).order_by('nombre')

    contexto = {
        'lista_productos': lista_productos_oferta, 
        'titulo_seccion': ' Ofertas y Promociones Vigentes'
    }

    
    return render(request, 'app_fruteria/ofertas.html', contexto)


# --------------------------------------------------------------------------
# B. VISTAS DE AUTENTICACIÓN
# --------------------------------------------------------------------------


def registro_usuario(request):
    """
    Maneja el registro de nuevos usuarios (inicios.html) usando un formulario seguro.
    """
    next_url = request.GET.get('next') 

    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, '¡Cuenta creada y sesión iniciada! Bienvenido a Olivos Verdes.')
            
            # --- CORREGIDO: Tu URL de compra se llama 'confirmar_compra' ---
            fallback_redirect = 'confirmar_compra' 
            return redirect(request.POST.get('next') or next_url or fallback_redirect)

        else:
            messages.error(request, 'Error en el registro. Por favor, verifica los datos.')
    else:
        form = RegistroClienteForm()

    contexto = {
        'form': form,
        'next': next_url
    }

    return render(request, 'app_fruteria/inicios.html', contexto)

def iniciar_sesion(request):
    """
    Maneja el inicio de sesión de usuarios existentes (login.html).
    """
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo! Sesión iniciada.')
                return redirect(request.POST.get('next') or 'menu_virtual')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    else:
        form = AuthenticationForm()
        
    form.fields['username'].label = 'Correo Electrónico'
    contexto = {'form': form}
    return render(request, 'app_fruteria/login.html', contexto)


@login_required 
def perfil_usuario(request):
    """ 
    Muestra y actualiza la información del perfil del usuario (perfil.html).
    """
    
    # Obtenemos el usuario y su perfil
    usuario = request.user
    try:
        # Aseguramos que el perfil se cree si no existe
        perfil, created = PerfilCliente.objects.get_or_create(user=usuario)
    except PerfilCliente.DoesNotExist:
        # Esto es un fallback, pero get_or_create debería manejarlo
        messages.error(request, 'Error crítico al cargar tu perfil.')
        return redirect('inicio')

    # --- Lógica de ACTUALIZACIÓN (POST) ---
    if request.method == 'POST':
        # 1. Obtenemos los datos del formulario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')

        # 2. Guardamos los datos en el modelo 'User'
        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.save()
        
        # 3. Guardamos los datos en el modelo 'PerfilCliente'
        perfil.telefono = telefono
        perfil.direccion = direccion
        perfil.save()
        
        # 4. Damos retroalimentación
        messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
        
        # Redirigimos a la misma página para ver los cambios
        return redirect('perfil')

    # --- Lógica de VISTA (GET) ---
    contexto = {
        'perfil': perfil,
        'usuario': usuario
    }
    return render(request, 'app_fruteria/perfil.html', contexto)

# en app_fruteria/views.py

def cerrar_sesion(request):
    """ 
    Cierra la sesión del usuario. 
    """
    logout(request)
    # La línea de 'messages' ha sido eliminada correctamente.
    return redirect('inicio')

# --------------------------------------------------------------------------
# C. VISTAS DEL CARRITO Y COMPRA (Lógica con Sesiones de Django)
# --------------------------------------------------------------------------

def agregar_al_carrito(request, producto_id):
    """ 
    Añade un producto al carrito, aplicando el precio final (con descuento).
    """
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    
    # Usamos el .precio_final (que ya calcula la oferta en models.py)
    precio_a_guardar = str(producto.precio_final)
    
    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] += 1
        cantidad_actual = carrito[producto_id_str]["cantidad"]
        carrito[producto_id_str]['precio'] = precio_a_guardar 
    else:
        carrito[producto_id_str] = {
            'cantidad': 1,
            'precio': precio_a_guardar
        }
        cantidad_actual = 1
        
    request.session['carrito'] = carrito
    request.session.modified = True 
    
    mensaje = f'✅ ¡{producto.nombre} añadido! Cantidad total: {cantidad_actual} kg.'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
        return JsonResponse({ 
            'success': True,
            'message': mensaje,
        })
    
    messages.success(request, mensaje)
    return redirect(request.META.get('HTTP_REFERER') or 'menu_virtual')

def ver_carrito(request):
    """
    Muestra los productos en el carrito (carrito.html) y calcula totales.
    """
    carrito = request.session.get('carrito', {})
    carrito_items = []
    
    # --- CORREGIDO: Usamos Decimal para todo el dinero ---
    total_general = Decimal('0.00')
    costo_envio = Decimal('40.00')
    
    for id_str, data in carrito.copy().items():
        try:
            producto = Producto.objects.get(pk=int(id_str))
            cantidad = int(data.get('cantidad', 0))
            precio = Decimal(data.get('precio', 0)) # Convertimos a Decimal
            
            subtotal = cantidad * precio
            total_general += subtotal
            
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
                'precio_unitario': precio, 
            })
            
        except (Producto.DoesNotExist, ValueError, TypeError, decimal.InvalidOperation):
            # Si el producto no existe o el precio está corrupto, lo borramos
            del carrito[id_str]
            request.session.modified = True
            messages.error(request, f"Error al leer un producto ID {id_str}. Eliminado del carrito.")

    request.session['carrito'] = carrito

    total_final = total_general + costo_envio if total_general > 0 else Decimal('0.00')

    contexto = {
        'carrito_items': carrito_items,
        'total_general': total_general,
        'costo_envio': costo_envio,
        'total_final': total_final, 
    }
    
    return render(request, 'app_fruteria/carrito.html', contexto)

# en app_fruteria/views.py

def _get_cart_totals(carrito_session):
    """
    Función de ayuda para recalcular los totales del carrito.
    """
    total_general = Decimal('0.00')
    costo_envio = Decimal('40.00') # Coincide con tu carrito.html
    
    for id_str, data in carrito_session.items():
        try:
            # No necesitamos golpear la BD, solo usamos los datos de la sesión
            cantidad = int(data.get('cantidad', 0))
            precio = Decimal(data.get('precio', 0))
            total_general += cantidad * precio
        except Exception:
            continue # Omitir items malformados

    total_final = total_general + costo_envio if total_general > 0 else Decimal('0.00')
    
    return {
        'subtotal': total_general,
        'total_final': total_final,
    }

# en app_fruteria/views.py

def ajustar_cantidad(request, producto_id, accion):
    
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    mensaje = "Error"
    success = False
    
    new_quantity = 0
    new_item_subtotal = Decimal('0.00')

    if producto_id_str in carrito:
        cantidad_actual = carrito[producto_id_str]['cantidad']
        precio_guardado = Decimal(carrito[producto_id_str]['precio']) 
        
        if accion == 'aumentar':
            new_quantity = cantidad_actual + 1
            mensaje = "Cantidad aumentada."
            success = True
            
        elif accion == 'disminuir':
            if cantidad_actual > 1:
                new_quantity = cantidad_actual - 1
                mensaje = "Cantidad disminuida."
                success = True
            else:
                # Si es 1 y le da a disminuir, lo dejamos en 1 (no lo borramos)
                new_quantity = 1
                mensaje = "La cantidad mínima es 1."
                success = False # No fue un éxito 'total', pero no es un error
        
        if success:
            carrito[producto_id_str]['cantidad'] = new_quantity
            request.session['carrito'] = carrito
            request.session.modified = True 
        
        # Calculamos el nuevo subtotal para ESE item
        new_item_subtotal = precio_guardado * new_quantity
    
    # --- LÓGICA DE RESPUESTA INTELIGENTE ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        # Calculamos los nuevos totales GLOBALES
        totals = _get_cart_totals(carrito) 
        
        return JsonResponse({
            'success': success, 
            'message': mensaje,
            # Datos para el JS
            'new_quantity': new_quantity,
            'new_item_subtotal': new_item_subtotal,
            'new_subtotal': totals['subtotal'], 
            'new_total_final': totals['total_final']
        })
    
    # Si no es AJAX, responde con un redirect (para enlaces normales)
    if success:
        messages.success(request, mensaje)
    else:
        messages.warning(request, mensaje)
        
    return redirect('ver_carrito')
# en app_fruteria/views.py



# ====================================================================
# --- FUNCIÓN TOTALMENTE CORREGIDA ---
# Esta es la función que estaba mal.
# Ahora usa Compra, DetalleCompra y Sucursal, como lo pide tu db.sqlite3
# ====================================================================

# en app_fruteria/views.py

@login_required 
def confirmar_compra(request):
    
    # --- Parte 1: Obtener carrito y perfil (para GET y POST) ---
    try:
        perfil_usuario = request.user.perfilcliente
    except PerfilCliente.DoesNotExist:
        perfil_usuario = None 

    carrito_session = request.session.get('carrito', {})
    
    # --- Parte 2: Lógica de PROCESAR PAGO (cuando se presiona "PAGAR") ---
    if request.method == 'POST':

        
        # A. Simulación de la pasarela
        tarjeta_ingresada = request.POST.get('numero_tarjeta', '')
        if not tarjeta_ingresada:
            messages.error(request, 'Por favor, ingresa un número de tarjeta para continuar.')
            return redirect('confirmar_compra')

        # B. Validación de Carrito y Perfil
        if not carrito_session:
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('menu_virtual')
        
        # Esta es la línea que falla
        if not perfil_usuario or not perfil_usuario.direccion: 
            messages.error(request, 'Por favor, completa tu dirección de envío en tu perfil.')
            return redirect('perfil')

        # C. ¡GUARDAR EN LA BASE DE DATOS (Forma correcta)!
        try:
            # ... (El resto de tu lógica de guardado de Compra se queda igual) ...
            
            # 1. Recalculamos el total y preparamos los items
            subtotal_pedido = Decimal('0.00')
            items_para_guardar = []
            
            for producto_id, item_data in carrito_session.items():
                producto = Producto.objects.get(id=producto_id)
                cantidad_real = int(item_data['cantidad'])
                precio_unitario = Decimal(item_data['precio'])
                
                subtotal_item = precio_unitario * cantidad_real
                subtotal_pedido += subtotal_item
                
                items_para_guardar.append({
                    'producto': producto,
                    'cantidad': cantidad_real,
                    'precio_unitario': precio_unitario
                })

            # 2. Asignamos la Sucursal
            sucursal_asignada = Sucursal.objects.first()
            if not sucursal_asignada:
                messages.error(request, 'Error del sistema: No hay sucursales configuradas.')
                return redirect('confirmar_compra')

            # 3. Crear el objeto Compra
            nueva_compra = Compra.objects.create(
                cliente=request.user,
                fecha_compra=timezone.now(),
                total_compra=subtotal_pedido,
                estado="Pagado",
                sucursal=sucursal_asignada
            )
            
            # 4. Crear los objetos DetalleCompra
            for item in items_para_guardar:
                DetalleCompra.objects.create(
                    compra=nueva_compra,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario']
                )
            
            # D. Limpia el carrito de la sesión
            del request.session['carrito']
            
            messages.success(request, '¡Tu pedido ha sido confirmado!')
            return redirect('orden_confirmada', pedido_id=nueva_compra.id)

        except Exception as e:
            messages.error(request, f'Error al guardar tu pedido: {e}')
            return redirect('confirmar_compra')

            
    # --- Parte 3: Lógica para MOSTRAR la página (petición GET) ---
    # (El resto de la función se queda igual)
    
    items_para_plantilla = []
    subtotal = Decimal('0.00')
    
    for producto_id, item_data in carrito_session.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            cantidad_real = int(item_data['cantidad'])
            precio_item = Decimal(item_data['precio']) 
            total_item = precio_item * cantidad_real
            subtotal += total_item
            
            items_para_plantilla.append({
                'producto': producto,
                'cantidad': cantidad_real,
                'subtotal': total_item, 
            })
        except (Producto.DoesNotExist, TypeError, KeyError, ValueError, decimal.InvalidOperation):
            continue
    
    costo_envio = Decimal('40.00') 
    total_con_envio = subtotal + costo_envio

    contexto = {
        'carrito_items': items_para_plantilla, 
        'total_general': subtotal,             
        'perfil': perfil_usuario,              
        'usuario': request.user,               
        'total_con_envio': total_con_envio,
        'costo_envio': costo_envio,
    }
    
    return render(request, 'app_fruteria/compra.html', contexto)

# ====================================================================
# --- FUNCIÓN CORREGIDA ---
# Ahora busca una 'Compra' en lugar de un 'Pedido'
# ====================================================================
@login_required
def orden_confirmada(request, pedido_id):
    try:
        # Buscamos una Compra que coincida con el ID y el cliente
        compra = Compra.objects.get(id=pedido_id, cliente=request.user)
        
        # También buscamos los detalles de esa compra
        detalles = DetalleCompra.objects.filter(compra=compra)
        
        contexto = { 
            'pedido': compra, # Pasamos la compra como 'pedido'
            'detalles': detalles # Pasamos los items
        }
        return render(request, 'app_fruteria/orden_confirmada.html', contexto)
    
    except Compra.DoesNotExist:
        messages.error(request, 'No se encontró ese pedido.')
        return redirect('menu_virtual')
    

def eliminar_item_carrito(request, producto_id):
    """
    Elimina un producto del carrito (compatible con AJAX y enlaces normales).
    """
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)
    mensaje = "Error"
    success = False

    if producto_id_str in carrito:
        del carrito[producto_id_str]
        request.session['carrito'] = carrito
        request.session.modified = True
        mensaje = "Producto eliminado del carrito."
        success = True
    else:
        mensaje = "Ese producto no estaba en tu carrito."
        success = False

    # --- LÓGICA DE RESPUESTA INTELIGENTE (ACTUALIZADA) ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        
        # ¡Calculamos los nuevos totales!
        totals = _get_cart_totals(carrito) 
        
        return JsonResponse({
            'success': success, 
            'message': mensaje,
            # Estas son las claves que tu JS está esperando:
            'new_subtotal': totals['subtotal'], 
            'new_total_final': totals['total_final']
        })

    # Si no es AJAX, responde con un redirect (para enlaces normales)
    if success:
        messages.success(request, mensaje)
    else:
        messages.warning(request, mensaje)

    return redirect('ver_carrito')
