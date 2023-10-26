from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('run-script', views.run_script, name='run_script'),
    path('login', views.login_view, name='login_view'),
    path('logout', views.logout, name='logout'),
    path('<str:page>', views.page, name='page'),



    # statics
    path('result/<str:id>', views.result, name='result'),
    path('css/<str:id>', views.cssLoader, name='cssLoader'),
    path('js/<str:id>', views.jsLoader, name='jsLoader'),
    path('images/<str:id>', views.imagesLoader, name='imagesLoader'),
    path('fonts/<str:id>', views.fontsLoader, name='fontsLoader'),
]


# Custom 404 error page configuration
handler400 = TemplateView.as_view(template_name='400.html')
handler401 = TemplateView.as_view(template_name='401.html')
handler404 = TemplateView.as_view(template_name='404.html')
handler500 = TemplateView.as_view(template_name='500.html')
