# en app_fruteria/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilCliente  # Importa el modelo que ya creaste
from django.db import transaction

# Esta es la clase que tu views.py está buscando
class RegistroClienteForm(UserCreationForm):
    
    # --- CAMPOS DEL MODELO USER ---
    email = forms.EmailField(required=True, label="Correo Electrónico")
    first_name = forms.CharField(max_length=100, required=True, label="Nombre")
    last_name = forms.CharField(max_length=100, required=True, label="Apellido")

    # --- CAMPOS DEL MODELO PERFILCLIENTE ---
    direccion = forms.CharField(max_length=255, required=True, label="Dirección de Entrega")
    telefono = forms.CharField(max_length=15, required=False, label="Teléfono")

    def __init__(self, *args, **kwargs):
        # Llama primero al __init__ original de UserCreationForm
        super().__init__(*args, **kwargs)
        
        # Accede al campo 'password1' y borra su texto de ayuda
        # En el __init__ de tu forms.py, usa esto en lugar de help_text = '':
        self.fields['password1'].help_text = 'Debe tener al menos 8 caracteres y no ser común.'
    

    class Meta(UserCreationForm.Meta):
        model = User
        # Define los campos del User que se usarán
        fields = ('username', 'email', 'first_name', 'last_name')

    @transaction.atomic
    def save(self, commit=True):
        # 1. Guarda el User
        user = super().save(commit=False)
        
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()

        # 2. Crea y guarda el PerfilCliente, enlazándolo al user
        PerfilCliente.objects.create(
            user=user, 
            direccion=self.cleaned_data.get('direccion'),
            telefono=self.cleaned_data.get('telefono')
        )
            
        return user