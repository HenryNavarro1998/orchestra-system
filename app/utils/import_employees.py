import openpyxl
from datetime import datetime, date
from ..models import Employee, AdminCollateral, AdminPosition, MusicalCenter

# Función de ayuda para limpiar y convertir valores. 
# Convierte cadenas vacías a None. Elimina espacios en blanco al inicio y al final.
def _clean_value(value):
    if value is None:
        return None
    stripped_value = str(value).strip()
    return stripped_value if stripped_value else None

# Función de ayuda para convertir a fecha de forma segura. 
# Convierte un valor a fecha, retornando None si falla o está vacío.
def _to_date(value, row):
    cleaned_value = _clean_value(value)
    if cleaned_value is None:
        return None

    # Caso 1: ya es datetime.date o datetime.datetime
    if isinstance(value, (datetime, date)):
        return value.date() if isinstance(value, datetime) else value

    # Caso 2: es string → intentamos varios formatos
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(cleaned_value, fmt).date()
        except ValueError:
            continue

    # Si ningún formato funcionó → warning
    print(f'Fecha inválida detectada: {value} - Fila: {row+2}. Se usará None.')
    return None

def import_employee_from_xlsx(file_obj):
    """
    Procesa un archivo XLSX y crea Empleados.
    Retorna estadísticas en un diccionario.
    """
    workbook = openpyxl.load_workbook(file_obj)
    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))
    header, data_rows = rows[0], rows[1:]

    expected_columns_xlsx = 12
    employees_created_count = 0
    import_errors = {}
    import_advices = {}
  
    
    # 1. Recorrer todas las filas del documento CSV. 
    for i, row in enumerate(data_rows):                   
        if len(row) < expected_columns_xlsx:
           import_advices[i+2] = f'Omitido por columnas faltantes por data'
           continue

        # 2. Normalizar a strings y limpiar valores
        values = [_clean_value(col) for col in row[:expected_columns_xlsx]]

        # 3. Extraer los 58 valores y limpiarlos de una vez. EL ORDEN IMPORTA
        (
            employee_code, 
            employee_document_id, 
            employee_fullname,
            employee_born_date,
            employee_id_admin_position,
            employee_id_admin_collateral,
            employee_id_musical_center,
            employee_admission_date,
            employee_proffesional,
            employee_type,
            employee_nationality,
            employee_gender,
        ) = values
        
        # 4. Convertir aquellos datos que deban convertirse (fechas y/o enteros)
        employee_born_date_clean           = _to_date(employee_born_date, i)
        employee_admission_date_clean      = _to_date(employee_admission_date, i)
        employee_lastnames, employee_names = employee_fullname.split(',')        

        # 5. OMITIR EMPLEADO SI LA FECHA DE NACIMIENTO O CÉDULA ES INVÁLIDO ---
        if not employee_born_date or not employee_document_id:
            import_advices[i+2] = f'Trabajador {employee_fullname} omitido porque su fecha de nacimiento o cédula es inválida o nula.'
            continue

        # 6. Buscar FK
        try:
            # Se buscan sus datos administrativos
            id_admin_position   = AdminPosition.objects.filter(code__icontains=employee_id_admin_position).first()
            id_admin_collateral = AdminCollateral.objects.filter(code__icontains=employee_id_admin_collateral).first()
            id_musical_center   = MusicalCenter.objects.filter(code__icontains=employee_id_musical_center).first()
            

            # 7. Se comprueba que exista su informacióm administrativa
            if id_admin_position and id_admin_collateral and id_musical_center:

                # --- 8. CREAR TRABAJADOR Y GUARDAR EL OBJETO CREADO ---
                try:
                    # get_or_create para no duplicar si el mismo empleado está en varias filas
                    employee_obj, created = Employee.objects.get_or_create(
                        # Campos clave de búsqueda
                        document_id = employee_document_id,
                        born_date   = employee_born_date_clean,     
                        defaults={
                            'code':           employee_code,    
                            'document_id':    employee_document_id,               
                            'names':          employee_names,               
                            'lastnames':      employee_lastnames,           
                            'born_date':      employee_born_date_clean,                
                            'admission_date': employee_admission_date_clean,                  
                            'proffesional':   False if employee_proffesional == "N" else True,                
                            'type':           employee_type,
                            'nationality':    employee_nationality,
                            'gender':         employee_gender,    
                            
                            # Asignar las FK
                            'id_admin_position':   id_admin_position,
                            'id_admin_collateral': id_admin_collateral,
                            'id_musical_center':   id_musical_center
                        }                            
                    )
                    if created:
                        employees_created_count += 1
                except Exception as e:
                    import_errors[i+2] = f"Error al crear el empleado {employee_fullname}: {e}"
                    employee_obj = None # Asegurarse de que employee_obj sea None si falla la creación

            # Si alguno de los datos administrativos no existe:   
            else:
                if not id_admin_position: 
                    import_errors[i+2] = f'{employee_fullname} omitido. Razón: Cargo administrativo  {employee_id_admin_position} n encontrado.'
                elif not id_admin_collateral:
                    import_errors[i+2] = f'{employee_fullname} omitido. Razón: Colateral {employee_id_admin_collateral} no encontrado.'   
                elif not id_musical_center:
                    import_errors[i+2] = f'{employee_fullname} omitido. Razón: Núcleo {employee_id_musical_center} no encontrado.'
                
        except Exception as e:
            import_errors[i+2] = f'Error al registrar al empleado {employee_fullname}: {e}'       

    return {
        "employees": employees_created_count,
        "import_errors": import_errors,
        "import_advices": import_advices
    }
