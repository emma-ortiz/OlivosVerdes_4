# en app_fruteria/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    """
    Este backend permite a los usuarios iniciar sesión
    usando su 'username' O su 'email'.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # El formulario de login siempre pasa el primer campo como 'username'
        # aunque nosotros le hayamos puesto la etiqueta 'Correo Electrónico'
        try:
            # Busca un usuario que coincida con el email O el username
            # 'iexact' significa 'ignorar mayúsculas/minúsculas'
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Si no se encuentra ningún usuario, falla la autenticación
            return None
        except User.MultipleObjectsReturned:
            # Si hay conflicto (raro), toma el primero
             user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).order_by('id').first()

        # Si encontramos un usuario, verificamos su contraseña
        if user and user.check_password(password):
            return user
        
        # Si la contraseña es incorrecta
        return None

    def get_user(self, user_id):
        # Esta parte es estándar y necesaria
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None