from django.db import models

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
	registro = models.TextField(verbose_name=('Registro sanitario'))
	medicina = models.ForeignKey(Medicina, related_name='formato',null=True, on_delete=models.CASCADE)

	def __str__(self):
		return "%s" % (self.presentacion)

class Tweet(models.Model):
	link = models.TextField(verbose_name=('Link'),unique=True)
	clasificacion = models.TextField(verbose_name=('Clasificacion'))
	medicina = models.ForeignKey(Medicina, related_name='Medicina', null=True, on_delete=models.CASCADE)

	def __str__(self):
		return "Link: %s Clasificacion: %s Medicina: %s" %(self.link,self.clasificacion,self.medicina)		