import requests 
from bs4 import BeautifulSoup 
import re 

# ver si existe find, sino usar regex para lo del color 

def webCrawler(url, medicine):
	sourceCode = requests.get(url, data = {'txtProducto' : medicine})
	plainText = sourceCode.text 
	soup = BeautifulSoup(plainText, 'html.parser')

	tableOfProducts = soup.find(id='productContainer')
	tds = tableOfProducts.findAll('td')

	info = collectInfo(tds)

	return info 

def collectInfo(tds):
	# Estructura products: {'farmacia': nombre, 'producto' : nombre, 'disponibles' : xxx}

	i = 6

	totalList = []

	while i < len(tds):

		if tds[i].get('class') and tds[i].get('class') == 'productNameStyle':   # algo pasa con el sentinela
			productRegex = re.split(r">|<", str(tds[i]))[10]

			i += 3

			#availabilityRegex = re.search(r"(.*) color:green (.*)", str(tds[i]))   # Revisar si es mejor
			availabilityRegex = re.split(r">|<", str(tds[i]))[13]

			if availabilityRegex == 'span style="color:green"':
				availability = 'Si'

			elif availabilityRegex == 'span style="color:yellow"':
				availability = 'Quedan pocos'

			elif availabilityRegex == 'span style="color:red"':    # Quiero ignorarlo en vez de hacer esto
				availability = 'No hay'

			product = {'farmacia': 'FullFarmacia', 'nombre' : productRegex, 'disponible' : availability}

			totalList.append(product)

		i += 2

	return totalList


def main():
	print(webCrawler('http://fullfarmacia.com/catalog.do?page=1&offSet=0&op=requestSearch&searchBox=atamel&go.x=0&go.y=0', 'atamel'))

if __name__ == "__main__":
	main()



