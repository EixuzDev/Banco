from rest_framework import serializers
from .models import Cliente, TipoCuenta, Cuenta, Transaccion, Servicio, PagoServicio

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
    
    def validated_client(self,data):
        nombre_completo = data.get('nombres')
        apellido_completo = data.get('apellidos')
        cedula_identidad = data.get('cedula')
        email = data.get('correo')

        if nombre_completo is not None and len(nombre_completo.split()) < 2:
            raise serializers.ValidationError({'nombres':'debe agregar el nombre completo'})
        if not nombre_completo.strip():
            raise serializers.ValidationError({'nombres':'no puede dejar este campo en blanco'})
        if apellido_completo is not None and len(apellido_completo.split()) < 2:
            raise serializers.ValidationError({'apellidos':'debe agregar el apellido completo'})
        if not apellido_completo.strip():
            raise serializers.ValidationError({'apellidos':'no puede dejar este campo en blanco'})
        if cedula_identidad is not None and len(cedula_identidad) < 7:
            raise serializers.ValidationError({'cedula':'la cedula tiene que tener al menos 7 digitos'})
        if '@' in email:
            raise serializers.ValidationError({'correo':'el correo debe contener un arroba'})
        
        return data
    
class TipoCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCuenta
        fields = '__all__'


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = '__all__'

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = '__all__'

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class PagoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoServicio
        fields = '__all__'
    