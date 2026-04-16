import openpyxl
from datetime import datetime, date
from ..models import Student, StudentRelative, EmergencyContact, OrchestralProject, Instrument, AcademicPeriod, MusicalProgram, MusicalCenter, DetailAcademicInscription

# Función de ayuda para limpiar y convertir valores. 
# Convierte cadenas vacías a None. Elimina espacios en blanco al inicio y al final.
def _clean_value(value):
    if value is None:
        return None
    stripped_value = str(value).strip()
    return stripped_value if stripped_value else None

# Función de ayuda para convertir a entero de forma segura. 
# Convierte un valor a entero, retornando None si falla o está vacío.
def _to_int(value, row):
    cleaned_value = _clean_value(value)
    if cleaned_value is not None:
        try:
            return int(cleaned_value)
        except ValueError:
            print(f'Valor no numérico detectado: {value} - Fila: {row+2}. Se usará None.')
    return None

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

def import_students_from_xlsx(file_obj):
    """
    Procesa un archivo XLSX y crea estudiantes, familiares, inscripciones y contactos de emergencia.
    Retorna estadísticas en un diccionario.
    """
    workbook = openpyxl.load_workbook(file_obj)
    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))
    header, data_rows = rows[0], rows[1:]

    expected_columns_xlsx = 58
    students_created_count = 0
    relatives_created_count = 0
    inscriptions_created_count = 0
    emergency_contacts_count = 0
    import_errors = {}
    import_advices = {}

    try:
        active_academic_period = AcademicPeriod.objects.get(is_active=True)
    except AcademicPeriod.DoesNotExist:
        # import_errors.append("No se encontró un período académico activo.")
        active_academic_period = None       

    
    # 2. Recorrer todas las filas del documento CSV. 
    for i, row in enumerate(data_rows):                   
        if len(row) < expected_columns_xlsx:
           import_advices[i+2] = f'Omitido por columnas faltantes por data'
           continue

        # Normalizar a strings y limpiar valores
        values = [_clean_value(col) for col in row[:expected_columns_xlsx]]

        # 3. Extraer los 58 valores y limpiarlos de una vez. EL ORDEN IMPORTA
        (
            student_lastnames, 
            student_names, 
            instrument_name,
            orchestral_project_name,
            musical_program_name,
            musical_center_name,
            student_gender, 
            student_born_date, 
            student_document_id, 
            student_home_phone, 
            student_cellphone, 
            student_email, 
            student_address, 
            legal_parent_fullname, 
            legal_parent_document_id, 
            legal_parent_relationship, 
            legal_parent_born_date, 
            legal_parent_marital_status, 
            legal_parent_profession, 
            legal_parent_home_phone, 
            legal_parent_cellphone, 
            legal_parent_office_phone, 
            legal_parent_email, 
            legal_parent_workplace, 
            legal_parent_job_title, 
            legal_parent_address, 
            relative_fullname, 
            relative_document_id, 
            relative_relationship, 
            relative_born_date, 
            relative_marital_status, 
            relative_profession, 
            relative_home_phone, 
            relative_cellphone, 
            relative_office_phone, 
            relative_workplace, 
            relative_job_title, 
            relative_address, 
            emergency_contact_1_name,
            emergency_contact_1_relationship,
            emergency_contact_1_phone,
            emergency_contact_2_name,
            emergency_contact_2_relationship,
            emergency_contact_2_phone,
            emergency_contact_3_name,
            emergency_contact_3_relationship,
            emergency_contact_3_phone,
            student_academic_degree, 
            student_academic_institution_name, 
            student_academic_institution_type, 
            student_academic_institution_address, 
            student_allergies, 
            student_regular_medical_treatment, 
            student_medical_report, 
            student_housing_type, 
            student_housing_condition, 
            student_number_people_living_housing,
            inscription_type
        ) = values
        
        # 4. Convertir aquellos datos que deban convertirse (fechas y/o enteros)
        student_born_date_imported                    = _to_date(student_born_date, i)
        student_number_people_living_housing_imported = _to_int(student_number_people_living_housing, i)
        legal_parent_born_date_imported               = _to_date(legal_parent_born_date, i)
        relative_born_date_imported                   = _to_date(relative_born_date, i)

        # 5. OMITIR ESTUDIANTE SI LA FECHA DE NACIMIENTO O CÉDULA ES INVÁLIDO ---
        if not student_born_date_imported or not student_document_id:
            import_advices[i+2] = f'Estudiante {student_names} {student_lastnames} omitido porque su fecha de nacimiento o cédula es inválida o nula.'
            continue

        # --- 6. PROCESAR REPRESENTANT LEGAL ---
        legal_parent_obj = None
        if legal_parent_document_id:
            try:
                # Se usa get_or_create para no duplicar si el mismo representante está en varias filas
                legal_parent_obj, created = StudentRelative.objects.get_or_create(
                    document_id=legal_parent_document_id,
                    defaults={
                        'relationship':   legal_parent_relationship,
                        'fullname':       legal_parent_fullname,
                        'born_date':      legal_parent_born_date_imported,
                        'marital_status': legal_parent_marital_status.capitalize(),
                        'nationality':    'V',
                        'profession':     legal_parent_profession,
                        'address':        legal_parent_address,
                        'home_phone':     legal_parent_home_phone,
                        'cellphone':      legal_parent_cellphone,
                        'email':          legal_parent_email,
                        'workplace':      legal_parent_workplace,
                        'job_title':      legal_parent_job_title,
                        'office_phone':   legal_parent_office_phone,
                    }
                )
                if created:
                    relatives_created_count += 1
            except Exception as e:
                import_errors[i+2] = f'Error al crear/obtener representante legal para el estudiante {student_names} {student_lastnames}: {e}'

        # --- 7. PROCESAR FAMILIAR SECUNDARIO ---
        relative_obj = None
        if relative_document_id:
            try:
                # Se usa get_or_create para no duplicar
                relative_obj, created = StudentRelative.objects.get_or_create(
                    document_id=relative_document_id,
                    defaults={
                        'relationship':   relative_relationship,
                        'fullname':       relative_fullname,
                        'born_date':      relative_born_date_imported,
                        'marital_status': relative_marital_status.capitalize(),
                        'nationality':    'V',
                        'profession':     relative_profession,
                        'address':        relative_address,
                        'home_phone':     relative_home_phone,
                        'cellphone':      relative_cellphone,
                        'email':          '',
                        'workplace':      relative_workplace,
                        'job_title':      relative_job_title,
                        'office_phone':   relative_office_phone,
                    }
                )
                if created:
                    relatives_created_count += 1
            except Exception as e:
                import_errors[i+2] = f'Error al crear/obtener familiar para el estudiante {student_names} {student_lastnames}: {e}'

        # --- 8. CREAR ESTUDIANTE Y GUARDAR EL OBJETO CREADO ---
        try:
            # get_or_create para no duplicar si el mismo estudiante está en varias filas
            student_obj, created = Student.objects.get_or_create(
                # Campos clave de búsqueda
                document_id = student_document_id,
                born_date   = student_born_date_imported, 
                email       = student_email,
                gender      = student_gender,             
                defaults={
                    'has_document_id':              False if student_document_id == "N/A" else True, 
                    'nationality':                  'V',
                    'names':                        student_names,
                    'lastnames':                    student_lastnames,
                    'address':                      student_address,
                    'home_phone':                   student_home_phone,
                    'cellphone':                    student_cellphone,
                    'academic_institution_name':    student_academic_institution_name,
                    'academic_institution_address': student_academic_institution_address,
                    'academic_degree':              student_academic_degree,
                    'academic_institution_type':    student_academic_institution_type,
                    'housing_type':                 student_housing_type,
                    'housing_condition':            student_housing_condition,
                    'number_people_living_housing': student_number_people_living_housing_imported,
                    'allergies':                    student_allergies,
                    'regular_medical_treatment':    student_regular_medical_treatment,
                    'medical_report':               student_medical_report,
                    
                    # Asignamos los objetos creados a las FK
                    'id_legal_parent'              : legal_parent_obj,
                    'id_relative'                  : relative_obj
                }                            
            )
            if created:
                students_created_count += 1
        except Exception as e:
            import_errors[i+2] = f"Error al crear el estudiante {student_names} {student_lastnames}: {e}"
            student_obj = None # Asegurarse de que student_obj sea None si falla la creación

        # --- 9. CREAR INSCRIPCIÓN Y CONTACTOS DE EMERGENCIA SOLO SI EL ESTUDIANTE FUE CREADO CORRECTAMENTE Y EXISTE PERÍODO ACADÉMICO ---
        if student_obj and active_academic_period:
            try:
                # Se busca el instrumento, nivel, programa y núcleo por nombre (busca una subcadena que coincida, insensible a mayúsculas o minúsculas)
                instrument_obj = Instrument.objects.filter(name__icontains=instrument_name).first()
                program_obj    = MusicalProgram.objects.filter(name__icontains=musical_program_name).first()
                center_obj     = MusicalCenter.objects.filter(name__icontains=musical_center_name).first()
                project_obj    = OrchestralProject.objects.filter(name__icontains=orchestral_project_name).first()
                
                # 10. Diccionario que contiene los contactos de Emergencia
                emergency_contacts_data = [
                    {
                        "fullname": emergency_contact_1_name,
                        "relationship": emergency_contact_1_relationship,
                        "cellphone": emergency_contact_1_phone
                    },
                    {
                        "fullname": emergency_contact_2_name,
                        "relationship": emergency_contact_2_relationship,
                        "cellphone": emergency_contact_2_phone
                    },
                    {
                        "fullname": emergency_contact_3_name,
                        "relationship": emergency_contact_3_relationship,
                        "cellphone": emergency_contact_3_phone
                    }
                ]

                # 11. Creación de los contactos de Emergencia
                # La función enumerate() da acceso tanto al índice como al contenido de cada elemento.
                for iterator, contact_data in enumerate(emergency_contacts_data, start=1):
                    # Solo los guarda si todos los campso son !=  None o != vacío
                    if not all(contact_data.values()):
                        import_advices[i+2] = f'Omitiendo contacto de emergencia #{iterator} por datos incompletos.'
                        continue  # omite este contacto si hay algún campo inválido
                    
                    emergency_contact_obj, created = EmergencyContact.objects.update_or_create(
                        fullname     = contact_data["fullname"],
                        relationship = contact_data["relationship"],
                        id_student   = student_obj,
                        defaults={
                            "cellphone": contact_data["cellphone"]
                        }
                    )
                    emergency_contacts_count += 1

                # 12. Se comprueba que exista el instrumento, el programa, nivel y núcleo, y se crea la inscripción
                if instrument_obj and project_obj and center_obj and program_obj:
                    inscription_obj, created = DetailAcademicInscription.objects.get_or_create(
                        # Campos clave de búsqueda
                        id_student         = student_obj,
                        id_academic_period = active_academic_period,
                        
                        # Campos de valores por defecto (solo si se crea un nuevo objeto)
                        defaults={
                            'id_orchestral_project': project_obj,
                            'id_instrument':         instrument_obj,
                            'id_musical_center':     center_obj,
                            'id_musical_program':    program_obj,
                            'inscription_date':      date.today(),
                            'type':                  inscription_type
                        }
                    )
                    if created:
                        inscriptions_created_count += 1
                    else:
                        import_errors[i+2] = f'{student_names} {student_lastnames} ya está inscrito en este período académico.'
                else:
                    if not instrument_obj: 
                        import_errors[i+2] = f'Estudiante {student_names} {student_lastnames} omitido. Razón: Instrumento {instrument_name} no encontrado.'
                    elif not project_obj:
                        import_errors[i+2] = f'Estudiante {student_names} {student_lastnames} omitido. Razón: Proyecto {orchestral_project_name} no encontrado.'   
                    elif not center_obj:
                        import_errors[i+2] = f'Estudiante {student_names} {student_lastnames} omitido. Razón: Núcleo {musical_center_name} no encontrado.'
                    elif not program_obj:
                        import_errors[i+2] = f'Estudiante {student_names} {student_lastnames} omitido. Razón: Programa {musical_program_name} no encontrado.'
                    
            except Exception as e:
                import_errors[i+2] = f'Error al registrar la inscripción para {student_names} {student_lastnames}: {e}'

    return {
        "students": students_created_count,
        "relatives": relatives_created_count,
        "inscriptions": inscriptions_created_count,
        "emergency_contacts": emergency_contacts_count,
        "import_errors": import_errors,
        "import_advices": import_advices
    }
