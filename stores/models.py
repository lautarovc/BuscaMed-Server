from django.db import models
from django.contrib.auth.models import User
from time import time 

# Create your models here.
class Activo(models.Model):
	componente = models.TextField(verbose_name=('Componente activo'),unique=True)

	def __str__(self):
		return "%s" % (self.componente)

class Medicina(models.Model):
	nombre = models.TextField(verbose_name=('Nombre de marca'))
	activo = models.ForeignKey(Activo, related_name='componente-activo+', null=True, on_delete=models.CASCADE)

	def __str__(self):
		return "%s" % (self.nombre)

class Presentacion(models.Model):
	presentacion = models.TextField(verbose_name=('Presentacion'))
	medicina = models.ForeignKey(Medicina, related_name='formato',null=True, on_delete=models.CASCADE)

	def __str__(self):
		return "%s %s" % (self.medicina,self.presentacion)

class ProductosPorTienda(models.Model):
	producto = models.ForeignKey(Presentacion, related_name='med', null=True, on_delete=models.CASCADE)
	tienda = models.ForeignKey(User, related_name='tienda', null=True, on_delete=models.CASCADE)
	disponibilidad = models.IntegerField(verbose_name=('Disponibilidad'))
	fechaDeIngreso = models.DateTimeField(verbose_name=('Fecha de actualizacion'), auto_now_add=True, blank=True)

	def __str__(self):
		return "Producto: %s Tienda: %s Disponibilidad: %s Fecha: %s" %(self.producto, self.tienda, self.disponibilidad, self.fechaDeIngreso.date())