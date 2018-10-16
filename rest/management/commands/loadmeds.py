import pandas as pd
from unidecode import unidecode
from django.core.management.base import BaseCommand, CommandError
from rest.models import Medicina, Activo, Presentacion
import time

class Command(BaseCommand):
	help = 'Loads medicines database'

	def add_arguments(self, parser):
		parser.add_argument('file', nargs='+', type=str)

	def handle(self, *args, **options):
		start = time.time()
		file = pd.read_csv(options['file'][0])
		tamano = len(file)
		print(tamano)
		diccComponente = {}
		diccMedicina = {}
		contador = 0

		for i in range(tamano):
			fila = file.iloc[i]
			aux_componente = fila['nombre-activo']
			#print(aux_componente)
			aux_componente = unidecode(aux_componente)
			#print(aux_componente)
			if aux_componente not in diccComponente:
				aux = Activo(componente=aux_componente)
				aux.save()
				diccComponente[aux_componente] = aux.id
				contador += 1
			else:
				aux = Activo.objects.get(componente=aux_componente)
			aux_nombre = fila['nombre-marca']
			aux_registro = fila['registro-sanitario']
			aux_presentacion = fila['presentacion']
			if aux_nombre not in diccMedicina:
				tmp = Medicina(nombre=aux_nombre,activo=aux)
				tmp.save()
				diccMedicina[aux_nombre] = tmp.id
			else:
				id_tmp = diccMedicina[aux_nombre]
				tmp = Medicina.objects.get(id=id_tmp)
				if tmp.activo != aux_componente:
					aux = Activo.objects.get(componente=aux_componente)
					tmp = Medicina(nombre=aux_nombre,activo=aux)
					tmp.save()
					diccComponente[aux_componente] = tmp.id

			var = Presentacion(presentacion=aux_presentacion,registro=aux_registro,medicina=tmp)
			var.save()

			#self.stdout.write(self.style.SUCCESS('Successfully added "%s"' % aux_nombre))

		print("CONTADOR: ",contador)
		print("diccMedicina",diccMedicina)
		print("diccComponente",diccComponente)
		end = time.time()	

		print("Final: ", end - start)