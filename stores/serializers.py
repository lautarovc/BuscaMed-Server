from rest_framework import serializers
from .models import *

class StoreSerializer(serializers.ModelSerializer):
	nombre = serializers.SerializerMethodField()
	direccion = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = ('nombre','direccion')
		read_only_fields = ('nombre','direccion')

	def get_nombre(self, obj):
		return obj.first_name

	def get_direccion(self, obj):
		return obj.last_name


class ActivoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Activo
		fields = ('componente',)
		read_only_fields = ('componente',)        

class MedicinaSerializer(serializers.ModelSerializer):
	activo = ActivoSerializer()

	class Meta:
		model = Medicina
		fields = ('nombre', 'activo')
		read_only_fields = ('nombre', 'activo')

class PresentacionSerializer(serializers.ModelSerializer):
	medicina = MedicinaSerializer()

	class Meta:
		model = Presentacion
		fields = ('presentacion', 'medicina')
		read_only_fields = ('presentacion', 'medicina')
        
class InventorySerializer(serializers.ModelSerializer):
	producto = PresentacionSerializer()
	tienda = StoreSerializer()

	class Meta:
		model = ProductosPorTienda
		fields = ('producto', 'tienda', 'disponibilidad', 'fechaDeIngreso')
		read_only_fields = ('producto', 'tienda', 'disponibilidad', 'fechaDeIngreso')