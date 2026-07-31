## SIstema Inventario Crypchange

Crear carpta de la virtualizacion
```
python3 -m venv venv
```

Inicia entorno virtual comando
```
source venv/bin/activate
```
Instala dependencias
```
pip install -r requirement.txt

```

Iniciar proyecto
```
python3 manage.py runserver
```

Busca el archivo config/settings.py y modifica
```
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
HOST': '10.20.22.3
``` 

Sync
```
venv/bin/python3 /tmp/sync_all_proveedor_columns.py
```