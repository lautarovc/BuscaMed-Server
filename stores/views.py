from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from .forms import LoginForm
from .models import *
import json 

# Create your views here.

class UserLoginView(LoginView):
	form_class = LoginForm

class StoresView(TemplateView):

	def get(self, request):
		if not request.user.is_authenticated:
			return redirect("/store/login");

		return render(request, 'readFile.html', {'success': -1})
		
	def post(self, request):
		if not request.user.is_authenticated:
			return redirect("/store/login");

		data = request.POST.get('csv')

		if data == None:
			return render(request, 'readFile.html', {'success': 0})

		data = json.loads(data)

		productosViejos = ProductosPorTienda.objects.filter(tienda=request.user).delete()

		for row in data:
			componenteMed = row['activo'].upper()
			activo = Activo.objects.filter(componente=componenteMed)

			if activo.count() == 0:
				activo = Activo.objects.create(componente=componenteMed)
			else:
				activo = activo[0]


			nombreMed = row['medicina'].upper()
			medicina = Medicina.objects.filter(nombre=nombreMed)

			if medicina.count() == 0:
				medicina = Medicina.objects.create(nombre=nombreMed, activo=activo)
			else:
				medicina = medicina[0]


			presentacionMed = row['presentacion'].upper()
			presentacion = Presentacion.objects.filter(presentacion=presentacionMed, medicina=medicina)

			if presentacion.count() == 0:
				presentacion = Presentacion.objects.create(presentacion=presentacionMed, medicina=medicina)
			else:
				presentacion = presentacion[0]


			disponibilidadMed = int(row['disponibilidad'])
			productosPorTienda = ProductosPorTienda.objects.create(producto=presentacion, tienda=request.user, disponibilidad=disponibilidadMed) 

		return render(request, 'readFile.html', {'success': 1})
