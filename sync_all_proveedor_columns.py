import sys, os, django

sys.path.insert(0, '/root/sistema_agenda')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection, models
from gestion.models import Proveedor

# Obtener campos definidos en el modelo Proveedor
model_fields = Proveedor._meta.fields

with connection.cursor() as cursor:
    # Mapeo de tipos de Django a tipos SQL de PostgreSQL
    for field in model_fields:
        col_name = field.column
        
        # Determinar el tipo de dato SQL correspondiente
        if isinstance(field, models.BooleanField):
            sql_type = "BOOLEAN DEFAULT FALSE"
        elif isinstance(field, (models.CharField, models.EmailField)):
            sql_type = f"VARCHAR({field.max_length if field.max_length else 255})"
        elif isinstance(field, models.TextField):
            sql_type = "TEXT"
        elif isinstance(field, models.IntegerField):
            sql_type = "INTEGER"
        elif isinstance(field, models.DecimalField):
            sql_type = f"NUMERIC({field.max_digits}, {field.decimal_places})"
        elif isinstance(field, models.DateTimeField):
            sql_type = "TIMESTAMP WITH TIME ZONE"
        elif isinstance(field, models.DateField):
            sql_type = "DATE"
        elif isinstance(field, models.ForeignKey):
            sql_type = "INTEGER"
        else:
            continue

        try:
            query = f'ALTER TABLE gestion_proveedor ADD COLUMN IF NOT EXISTS {col_name} {sql_type};'
            cursor.execute(query)
            print(f"✔️ Columna '{col_name}' verificada/agregada.")
        except Exception as e:
            print(f"⚠️ Error agregando '{col_name}': {e}")

print("\n✅ Todas las columnas de gestion_proveedor sincronizadas correctamente.")
