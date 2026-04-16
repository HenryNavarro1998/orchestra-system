from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import OrchestralProject, AcademicPeriod, DetailAcademicInscription
from django.db.models import Count, Q


@login_required
def orchestral_projects_list(request):

    projects = OrchestralProject.objects.annotate(
        inscripciones_activas=Count(
            'detailacademicinscription',
            filter=Q(detailacademicinscription__id_academic_period__is_active=True)
        )
    )

    # paginated_projects = paginate(request, projects, per_page=10)
    
    return render(request, 'orchestral_projects/orchestral_projects_list.html', {
        'page_obj': projects
    }) 
        

@login_required
def orchestral_projects_detail(request, id):
    orchestral_project = get_object_or_404(OrchestralProject, id=id)    
    inscriptions = DetailAcademicInscription.objects.filter(
            id_orchestral_project=orchestral_project, 
            id_academic_period__is_active=True
        )
    
    period_active = AcademicPeriod.objects.filter(is_active=True).first()

    return render(request, 'orchestral_projects/orchestral_project_detail.html', {
        'orchestral_project': orchestral_project,
        'inscriptions': inscriptions,
        'academic_period': period_active
    }) 