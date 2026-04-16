from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.contrib.staticfiles.finders import find
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from ..models import Employee
from ..utils.calculate_age import calculate_age
from ..utils.import_employees import import_employee_from_xlsx
import os

# Create your views here.
@login_required
def employee_list(request):
    employees = Employee.objects.all()

    # Recupera errores si hubo previamente una importación y luego los elimina
    import_errors = request.session.pop('import_errors', None)
    import_advices = request.session.pop('import_advices', None)

    # paginated_employees = paginate(request, employees, per_page=10)
    
    return render(request, 'employees/employee_list.html', {
        'page_obj': employees,
        'import_errors':  import_errors,  # Pasa los errores al template
        'import_advices': import_advices,
        
    })

@login_required
def employee_detail(request, id):
    employee = get_object_or_404(Employee, id=id)

    employee.calculated_age = calculate_age(employee.born_date)

    return render(request, 'employees/employee_detail.html', {
        'employee': employee
    }) 

@login_required
def download_employees_template(request):
    file_path = find(os.path.join('employees', 'templates', 'template_employees.xlsx'))
    
    if not file_path:
        raise Http404("Template de empleados no encontrado.")
    
    # Abre el archivo en modo binario
    file_to_download = open(file_path, 'rb')
    
    # Crea una respuesta de archivo, forzando la descarga con Content-Disposition
    response = FileResponse(file_to_download)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename="template_employees.xlsx"'
    
    return response

@login_required
@require_POST
def upload_employees_data(request):
    file = request.FILES.get("file")
    if not file:
        messages.error(request, "Debes seleccionar un archivo de excel")
        return redirect("employees:list")

    try:
        # Llamamos a la lógica central de importación y obtenemos el resultado completo
        result = import_employee_from_xlsx(file)
        
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
            messages.success(request, f"¡Importación completada! {result['employees']} empleados registrados, "
                                      f"Errores: {result['import_errors']}."
                                      f"Advertencias: {result['import_advices']}."
                            )
        
        
    except Exception as e:
        # Error a nivel de archivo
        messages.error(request, f"Error al importar el archivo: {e}")

    return redirect("employees:list")