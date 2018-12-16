import requests 
from bs4 import BeautifulSoup 
import re 

def webCrawler(url, medicine):
	sourceCode = requests.post(url, data = {'producto' : medicine, 'estado' : '', 'lugar' : ''}, timeout=60)
	plainText = sourceCode.text 
	soup = BeautifulSoup(plainText, 'html.parser')

	tds = soup.find_all('td')

	info = collectInfo(tds)
	
	return info

def collectInfo(tds):
	# Estructura store: {'farmacia': 'Farmarket', 'sede' : nombre, 'productos' : productosPorTienda} 
	# Estructura products: {'producto' : nombre, 'disponibles' : xxx}

	i = 0

	totalList = []       
	productsByLocation = []

	while i < len(tds):
		state = re.split(r">|<", str(tds[i+3]))[2]
		location = re.split(r">|<", str(tds[i+4]))[2]
		currentlocation = location

		while i < len(tds) and location == currentlocation:
			productRegex = re.split(r">|<", str(tds[i]))[2].strip()
			products = {'nombre': productRegex, 'disponibles': 'Si'}
			productsByLocation.append(products)

			i += 6

			if i < len(tds):
				currentlocation = re.split(r">|<", str(tds[i+4]))[2]

		store = {'farmacia': 'Fundafarmacia', 'sede' : location +", "+state, 'productos' : productsByLocation}

		totalList.append(store)

		productsByLocation = []

	return totalList

def main():
	print(webCrawler('http://www.fundafarmacia.com/consulta/busqueda.php', 'atamel'))

if __name__ == "__main__":
	main()



