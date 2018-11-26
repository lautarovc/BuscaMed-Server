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
	i = 0

	#while i < len(tds):
	productRegex = re.split(r">|<", str(tds[i]))
	print(productRegex)


def main():
	print(webCrawler('http://www.fundafarmacia.com/index.php/productos/', 'atamel'))

if __name__ == "__main__":
	main()



