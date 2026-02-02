from django.urls import path
from app.views import home, CustomLoginView, signout

urlpatterns = [
    path('', home, name="home"),
    path('login', CustomLoginView.as_view(), name='login'),
    path('logout', signout, name='logout'),
]
