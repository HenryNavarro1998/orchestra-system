from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import MusicalProgram, DetailAcademicInscription, AcademicPeriod
from django.db.models import Count, Q


@login_required
def programs_list(request):

    programs = MusicalProgram.objects.annotate(
        inscripciones_activas=Count(
            'detailacademicinscription',
            filter=Q(detailacademicinscription__id_academic_period__is_active=True)
        )
    )

    #paginated_programs = paginate(request, programs, per_page=10)
    
    return render(request, 'musical_programs/musical_programs_list.html', {
        'page_obj': programs
    }) 

@login_required
def program_detail(request, id):
    musical_program = get_object_or_404(MusicalProgram, id=id)    
    inscriptions = DetailAcademicInscription.objects.filter(
            id_musical_program=musical_program, 
            id_academic_period__is_active=True
        )
    
    period_active = AcademicPeriod.objects.filter(is_active=True).first()

    return render(request, 'musical_programs/musical_program_detail.html', {
        'musical_program': musical_program,
        'inscriptions': inscriptions,
        'academic_period': period_active
    }) 
