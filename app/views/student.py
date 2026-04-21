from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..models import Student, EmergencyContact, StudentRelative, DetailAcademicInscription, OrchestralProject, Instrument, AcademicPeriod
from ..utils.calculate_age import calculate_age
from ..utils.import_students import import_students_from_xlsx  

@login_required
def student_list(request):
    #Mejorar a futuro para que la vista no explote si no hay períodos académicos
    current_academic_period = get_object_or_404(AcademicPeriod, is_active=True)

    # Al listado de estudiante se le agregan los campos del instrumento y proyecto que tiene
    # vinculado en su inscripción. Adicionalmente solo se obtienen estudiantes cuya
    # inscripción esté vinculada al período académico en curso.
    students = Student.objects.filter(
        detailacademicinscription__id_academic_period = current_academic_period
    ).annotate(
        instrument         = F('detailacademicinscription__id_instrument__name'),
        orchestral_project = F('detailacademicinscription__id_orchestral_project__name'), 
        musical_program    = F('detailacademicinscription__id_musical_program__name'), 
        musical_center    = F('detailacademicinscription__id_musical_center__name'), 
    ).distinct()

    all_students_count = students.count()
    all_instruments = Instrument.objects.all()
    all_projects = OrchestralProject.objects.all()

    # Recupera errores si hubo previamente una importación y luego los elimina
    import_errors = request.session.pop('import_errors', None)
    import_advices = request.session.pop('import_advices', None)
    
    context = {
        'students':                students,
        'all_students':            all_students_count,
        'all_instruments':         all_instruments.count(),
        'all_projects':            all_projects.count(),
        'current_academic_period': current_academic_period,
        'import_errors':           import_errors,  # Pasa los errores al template
        'import_advices':          import_advices
    }

    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, id):
    student = get_object_or_404(Student, id=id)
    legal_parent = student.id_legal_parent  # Esto es una instancia de StudentRelative
    relative = student.id_relative          # También es una instancia de StudentRelative
    inscriptions = DetailAcademicInscription.objects.filter(id_student=student)
    emergency_contacts = EmergencyContact.objects.filter(id_student=student)

    # Calcular las edades
    student.calculated_age = calculate_age(student.born_date)

    if legal_parent and legal_parent.born_date:
        legal_parent.calculated_age = calculate_age(legal_parent.born_date)
    
    if relative and relative.born_date:
        relative.calculated_age = calculate_age(relative.born_date)

    return render(request, 'students/student_detail.html', {
        'student':            student,
        'legal_parent':       legal_parent,
        'relative':           relative,
        'inscriptions':       inscriptions,
        'emergency_contacts': emergency_contacts
    }) 

@login_required
def download_students_template(request):
    file_path = finders.find('templates/template_students.xlsx')
    
    if not file_path:
        raise Http404("Plantilla de estudiantes no encontrada.")
    
    # Abre el archivo en modo binario
    file_to_download = open(file_path, 'rb')
    
    # Crea una respuesta de archivo, forzando la descarga con Content-Disposition
    response = FileResponse(file_to_download)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename="template_students.xlsx"'
    
    return response

@login_required
@require_POST
def upload_students_data(request):
    file = request.FILES.get("file")
    if not file:
        messages.error(request, "Debes seleccionar un archivo de excel")
        return redirect("app:student_list")

    try:
        # Llamamos a la lógica central de importación y obtenemos el resultado completo
        result = import_students_from_xlsx(file)
        
        # Obtener los diccionarios de errores y avisos
        errors = result.get('import_errors', {})
        advices = result.get('import_advices', {})

        if errors:
            # Si hay errores, los agregamos a la sesión para recuperarlos en la vista 'list'
            request.session['import_errors'] = errors
            messages.error(request, "Algunos registros no pudieron ser importados.")
        if advices:
            request.session['import_advices'] = advices
            if not errors:
                messages.warning(request, "La importación se completó con algunas advertencias. Revisa los detalles.")
        if not advices and not errors:
            # Si no hay errores
            messages.success(request, f"¡Importación completada! {result['students']} estudiantes creados, "
                                      f"{result['relatives']} familiares y {result['inscriptions']} inscripciones. "
                                      f"Errores: {result['import_errors']}."
                                      f"Advertencias: {result['import_advices']}."
                            )
        
        
    except Exception as e:
        # Error a nivel de archivo
        messages.error(request, f"Error al importar el archivo: {e}")

    return redirect("app:student_list")