
function checkData(data) {
	var firstRow = data[0]
	
	if (!("activo" in firstRow && "medicina" in firstRow && "presentacion" in firstRow && "disponibilidad" in firstRow)) {
		return false;
	}
	
	return true;
}

function readCSV() {
	var file = document.getElementById("fileName").files[0];
	
	// Revisamos que sea un archivo CSV.
	var fileType = file.name.split('.').pop();
	
	if (fileType != "csv") {
		// PONER AQUI MENSAJE DE ARCHIVO NO ES CSV
		alert("Error: El archivo no es un .csv");
		return;
	}

	// Leemos archivo
	var reader = new FileReader();
	reader.readAsText(file);

	reader.onload = function(event){

		// Cargamos texto del CSV y revisamos que separador tiene
    	var csv = event.target.result;
    	var firstLine = csv.split('\n').shift();

    	if (firstLine.includes(";")) {
    		var options = {"separator" : ";"};
    	}
    	else if (firstLine.includes(",")) {
    		var options = {"separator" : ","};
    	}
    	else {
    		alert("Error: check csv separator");
    		return;
    	}

    	// Convertimos a arreglo de diccionarios
    	var data = $.csv.toObjects(csv, options); 

    	// Revisamos que tenga las columnas necesarias
    	var dataIntegrity = checkData(data);

    	if (!dataIntegrity) {
    		// PONER AQUI MENSAJE DE ARCHIVO INADECUADO
    		alert("Error: columns not correct");
    		return;
    	}

    	// En caso contrario, convertimos a json string y enviamos
    	var dataString = JSON.stringify(data);

    	console.log(dataString);

			document.getElementById("csv").value = dataString;
			$('#formButton').click();
	}
	reader.onerror = function(){ alert('Unable to read ' + file.fileName); };
}

function instructions() {

	alert("Debe subir un archivo .csv que tenga las siguientes columnas: activo, medicina, presentacion y disponibilidad. Puede contener otras columnas, pero las anteriores deben aparecer con dichos nombres.");
	return;
}