from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("professor/", views.pagina_professor, name="pagina_professor"),
    path("aluno/", views.pagina_aluno, name="pagina_aluno"),
    path("professor/material/", views.upload_material, name="upload"),
    path("material/<int:material_id>/", views.visualizar_material, name="visualizar_material"),
    path("ano/criar/", views.criar_ano, name="criar_ano"),
    path("semestre/criar/", views.criar_semestre, name="criar_semestre"),
    path("disciplina/criar/", views.criar_disciplina, name="criar_disciplina"),
    path("turma/criar/", views.criar_turma, name="criar_turma"),
    path("turma/entrar/", views.entrar_turma, name="entrar_turma"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
