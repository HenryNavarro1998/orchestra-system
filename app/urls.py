from django.urls import path
from app.views import home, CustomLoginView, signout
from . import views
from .views import instrument, orchestral_project, musical_program, musical_center
urlpatterns = [
    path('', home, name="home"),
    path('login', CustomLoginView.as_view(), name='login'),
    path('logout', signout, name='logout'),

    # academic core
    path('orchestral_projects',          orchestral_project.orchestral_projects_list, name='project_list'),
    path('orchestral_projects/<int:id>', orchestral_project.orchestral_projects_detail, name='project_detail'),
    path('musical_programs',             musical_program.programs_list, name='programs_list'),
    path('musical_programs/<int:id>',    musical_program.program_detail, name='program_detail'),
    path('instruments',                  instrument.instruments_list, name='instruments_list'),
    path('instruments/<int:id>',         instrument.instrument_detail, name='instrument_detail'),
    path('musical_center',               musical_center.center_list, name='center_list'),
    path('musical_center/<int:id>',      musical_center.center_detail, name='center_detail'),
]
