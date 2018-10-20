from rest_framework import serializers
from .models import *

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
        
class TweetSerializer(serializers.ModelSerializer):
	medicina = MedicinaSerializer()

	class Meta:
		model = Tweet
		fields = ('link', 'medicina')
		read_only_fields = ('link', 'medicina')