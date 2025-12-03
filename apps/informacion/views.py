from django.shortcuts import render
from django.db import transaction
from django.db.models import ProtectedError
from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Cliente, TipoCuenta, Cuenta, Transaccion, Servicio, PagoServicio
from .serializer import ClienteSerializer, TipoCuentaSerializer, CuentaSerializer, TransaccionSerializer, ServicioSerializer, PagoServicioSerializer
from .exceptions import FondosInsuficiente, CuentaInactiva, IdentidadInvalidad

# Create your views here.
@api_view(['GET','POST'])

def register_client(request):
    
    if request.method=='GET':
        try:
            client = Cliente.objects.all()
            serializer = ClienteSerializer(client, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':'Error de registro', 'detalles':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                serializer = ClienteSerializer(data = request.data)
                if serializer.is_valid():
                    serializer.save()
                return Response({'Mensaje':'Creado Correctamente'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':'Error interno del servidor', 'detalles':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET','PUT','DELETE'])

def update_client(request,pk):
    try:
        client = Cliente.objects.select_for_update().get(pk=pk)
    except Cliente.DoesNotExist:
        return Response({'Error':'Lista no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'Error':'Error al obtener registro', 'detalles':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if request.method == 'GET':
        serializer = ClienteSerializer(client)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = ClienteSerializer(client, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'Mensaje':'Lista actualizada correctamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        try:
            with transaction.atomic():
                client.delete()
                return Response({'Mensaje':'Eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError as e:
            return Response({'Error':'Error registro protegido!', 'detalles':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error':'Error al eliminar registro', 'detalle':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])

def types_account(request):
    try:
        with transaction.atomic():
            serializer = TipoCuentaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'Mensaje': 'Creado Correctamente'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'Error': 'Error interno', 'detalle': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])

def types_services(request):
    try:
        with transaction.atomic():
            serializer = ServicioSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'Mensaje': 'Creado Correctamente'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'Error': 'Error interno', 'detalle': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        
@api_view(['POST'])
def open_account(request):
    try:
        with transaction.atomic():

            cliente_id = request.data.get('cliente')
            tipo_cuenta = request.data.get('tipo_cuenta')
            saldo_inicial = request.data.get('saldo_inicial',0)

        #1 Validar el cliente
        try:
            cliente = Cliente.objects.get(id_client=cliente_id)
        except Cliente.DoesNotExist:
            raise IdentidadInvalidad({'ID':'Este cliente no existe'})
        
        #2 Crear la cuenta del cliente
        cuenta = Cuenta.objects.create(
            cliente = cliente,
            tipo_cuenta_id = tipo_cuenta, 
            saldo=saldo_inicial,
            )
        #3 Registrar transaccion de apertura
        Transaccion.objects.create(
            cuenta_destino = cuenta,
            monto =saldo_inicial,
            tipo="Apertura",
            descripcion ="Apertura de cuenta con saldo inicial"
        )

        return Response(CuentaSerializer(cuenta).data, status=status.HTTP_201_CREATED)
    
    except IdentidadInvalidad as e:
        return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'Error':'Error interno', 'detalle':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])

def transfer(request):
    try:
        with transaction.atomic():
            origen_id = request.data.get('cuenta_origen')
            destino_id = request.data.get('cuenta_destino')
            monto = Decimal(request.data.get('monto',0))


            origen = Cuenta.objects.select_for_update().get(id=origen_id)
            destino = Cuenta.objects.select_for_update().get(id=destino_id)

            if not origen.activa:
                raise CuentaInactiva('La cuenta origen esta inactiva')
            
            if not destino.activa:
                raise CuentaInactiva('La cuenta destino esta inactiva')
            
            if origen.saldo < monto:
                raise FondosInsuficiente('Fondo insuficiente en cuenta origen')
            
            origen.saldo -= monto
            destino.saldo +=monto

            origen.save()
            destino.save()

            Transaccion.objects.create(
                cuenta_origen = origen,
                cuenta_destino = destino,
                monto = monto,
                tipo="TRANSFERENCIA",
                descripcion="Transferencia entre cuentas"
            )

            return Response({'Mensaje':'Transferencia realizada con exito'})
        
    except FondosInsuficiente as e:
        return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except CuentaInactiva as e:
        return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error':'Error interno', 'detalles':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def pay_service(request):
    try:
        cliente_id = request.data.get('cliente')
        tipo_servicio = request.data.get('servicio')
        origen_id = request.data.get('cuenta_origen')
        pago_servicio=Decimal(request.data.get('monto',0))
        try:
            client = Cliente.objects.get(id_client=cliente_id)
        except Cliente.DoesNotExist:
            raise IdentidadInvalidad({'ID':'Este cliente no existe'})

        origen = Cuenta.objects.select_for_update().get(id=origen_id)
        servicio = Servicio.objects.select_for_update().get(id=tipo_servicio)

        if not origen.activa:
            raise CuentaInactiva('Cuenta inactiva')
        
        if origen.saldo < pago_servicio:
            raise FondosInsuficiente('Fondo Insuficiente en cuenta origen')
        
        origen.saldo -= pago_servicio
        servicio.saldo += pago_servicio

        origen.save()
        servicio.save()

        Transaccion.objects.create(
            cuenta_origen = origen,
            tipo = "Pago_Servicio",
            monto= pago_servicio,
            descripcion = "Pago de Servicios"
        )
        return Response({'Mensaje':'Pago del servicio realizada con exito'})
    except FondosInsuficiente as e:
        return Response({'Error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except CuentaInactiva as e:
        return Response({'Error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'Error': 'Error interno', 'detalles':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])

def show_account(request,pk):
    try:
        cuenta = Cuenta.objects.select_for_update().get(pk=pk)
        serializer = CuentaSerializer(cuenta)
        return Response(serializer.data)
    except Cuenta.DoesNotExist:
        return Response({'Error':'La cuenta no existe'}, status=status.HTTP_404_NOT_FOUND)

