from django.db import models

# Create your models here.
class Cliente(models.Model):
    id_client = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=150)
    apellidos= models.CharField(max_length=150)
    cedula = models.CharField(max_length=8)
    correo = models.EmailField()
    fecha = models.DateTimeField(auto_now_add=True)


class TipoCuenta(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion= models.TextField(null=True,blank=True)


class Cuenta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="cuentas")
    tipo_cuenta= models.ForeignKey(TipoCuenta, on_delete=models.PROTECT)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)


class Servicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2,default=0)


class Transaccion(models.Model):
    cuenta_origen = models.ForeignKey(Cuenta,null= True, blank= True, on_delete=models.SET_NULL, related_name="transaccion_saliente")
    cuenta_destino = models.ForeignKey(Cuenta,null= True, blank= True, on_delete=models.SET_NULL, related_name="transaccion_entrante")

    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=50) # Apertura, Transferencia, Pago servicio, Prestamo
    descripcion = models.TextField(blank=True, null= True)
    fecha = models.DateTimeField(auto_now_add=True)

class PagoServicio(models.Model):
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)