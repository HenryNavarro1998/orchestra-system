from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import DetailAcademicInscription, AcademicPeriod, MusicalCenter
from django.db.models import Count, Q


@login_required
def center_list(request):

    musical_center = MusicalCenter.objects.annotate(
        inscripciones_activas=Count(
            'detailacademicinscription',
            filter=Q(detailacademicinscription__id_academic_period__is_active=True)
        )
    )

    #paginated_musical_center = paginate(request, musical_center, per_page=10)
    
    return render(request, 'musical_center/musical_center_list.html', {
        'page_obj': musical_center
    }) 

@login_required
def center_detail(request, id):
    musical_center = get_object_or_404(MusicalCenter, id=id)    
    inscriptions = DetailAcademicInscription.objects.filter(
            id_musical_center = musical_center, 
            id_academic_period__is_active=True
        )
    
    period_active = AcademicPeriod.objects.filter(is_active=True).first()

    return render(request, 'musical_center/musical_center_detail.html', {
        'musical_center': musical_center,
        'inscriptions': inscriptions,
        'academic_period': period_active
    }) 
