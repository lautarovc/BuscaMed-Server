import requests
from bs4 import BeautifulSoup
import re

def webCrawler(url, medicine):
	sourceCode = requests.post(url, data = {'txtProducto' : medicine})
	plainText = sourceCode.text 
	soup = BeautifulSoup(plainText, 'html.parser')

	tds = soup.find_all('td')

	info = collectInfo(tds)
	
	return info

def collectInfo(tds):
	# Estructura store: {'farmacia': 'Farmarket', 'sede' : nombre, 'productos' : productosPorTienda} 
	# Estructura products: {'producto' : nombre, 'disponibles' : xxx}
	
	i = 3 

	totalList = []       
	productsByStore = []
	
	while i < len(tds):
		if tds[i].get('class')[0] == 'CeldaCentradaTextoBlanco' and tds[i].get('colspan') == '2':
			storeLocation = re.split(r':|[|]', tds[i].string)[1].strip()
		
			i += 3 

			while i < len(tds) and tds[i].get('class')[0] == 'FondoTabla':
				productRegex = re.split(r">|<", str(tds[i]))[2]
				product = {'nombre' : productRegex, 'disponibles' : int(tds[i+1].string)}
				productsByStore.append(product)

				i += 2

			store = {'farmacia': 'Farmarket', 'sede' : storeLocation, 'productos' : productsByStore}

			totalList.append(store)

			productsByStore = []

	return totalList

def main():
	print(webCrawler('https://www.farmarket.com.ve/sitio/index.php/resultados-busqueda-productos/', 'atamel'))

if __name__ == "__main__":
	main()



