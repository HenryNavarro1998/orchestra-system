from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Instrument, AcademicPeriod, DetailAcademicInscription
from django.db.models import Count, Q


@login_required
def instruments_list(request):

    instruments = Instrument.objects.annotate(
        inscripciones_activas=Count(
            'detailacademicinscription',
            filter=Q(detailacademicinscription__id_academic_period__is_active=True)
        )
    )

    # paginated_instruments = paginate(request, instruments, per_page=10)
    
    return render(request, 'instruments/instruments_list.html', {            
            'page_obj': instruments
    }) 
    

@login_required
def instrument_detail(request, id):
    instrument = get_object_or_404(Instrument, id=id)    
    inscriptions = DetailAcademicInscription.objects.filter(
            id_instrument=instrument, 
            id_academic_period__is_active=True
        )
    
    period_active = AcademicPeriod.objects.filter(is_active=True).first()

    return render(request, 'instruments/instrument_detail.html', {
        'instrument': instrument,
        'inscriptions': inscriptions,
        'academic_period': period_active
    }) 
