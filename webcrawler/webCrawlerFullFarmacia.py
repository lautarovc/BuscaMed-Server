import requests 
from bs4 import BeautifulSoup 
import re 

# ver si existe find, sino usar regex para lo del color 

def webCrawler(medicine):
	url = 'http://fullfarmacia.com/catalog.do?page=1&offSet=0&op=requestSearch&searchBox='+medicine+'&go.x=0&go.y=0'

	sourceCode = requests.get(url)
	plainText = sourceCode.text 
	soup = BeautifulSoup(plainText, 'html.parser')

	tableOfProducts = soup.find(id='productContainer')
	tds = tableOfProducts.findAll('td')

	info = collectInfo(tds)

	return info 

def collectInfo(tds):
	# Estructura store: {'farmacia': 'FullFarmacia', 'Colinas de Bello Monte' : nombre, 'productos' : products} 
	# Estructura products: {'producto' : nombre, 'disponible' : disponibilidad}

	i = 6

	totalList = []
	productsByStore = []

	while i < len(tds):

		if tds[i].get('class')[0] == 'productNameStyle':   
			productRegex = re.split(r">|<", str(tds[i]))[10].strip()

			i += 3

			availabilityRegex = re.split(r">|<", str(tds[i]))[13]

			if availabilityRegex == 'span style="color:green"':
				availability = 'Si'

			elif availabilityRegex == 'span style="color:yellow"':
				availability = 'Quedan pocos'

			elif availabilityRegex == 'span style="color:red"':    
				i += 2
				continue 

			product = {'nombre' : productRegex, 'disponibles' : availability}
			productsByStore.append(product)

			i += 2

	store = {'farmacia': 'FullFarmacia', 'sede' : 'Colinas de Bello Monte', 'productos' : productsByStore}
	totalList.append(store)

	return totalList


def main():
	print(webCrawler('atamel'))

if __name__ == "__main__":
	main()



