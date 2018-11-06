from django.shortcuts import render
from django.views.generic import TemplateView
import json 

# Create your views here.

class StoresView(TemplateView):

	def get(self, request):
		return render(request, 'readFile.html', {})
		
	def post(self, request):
		data = request.POST.get('csv')

		if data == None:
			return render(request, 'readFile.html', {})

		data = json.loads(data)

		


		return render(request, 'readFile.html', {})
