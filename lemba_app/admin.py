from django.contrib import admin

from .models import Ano, Disciplina, Inscricao, Material, Perfil, Semestre, Turma


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "tipo")
    list_filter = ("tipo",)
    search_fields = ("user__username", "user__email")

    @admin.display(description="Utilizador")
    def username(self, obj):
        if obj.user_id:
            return getattr(obj.user, "username", "Utilizador removido")
        return "Sem utilizador"


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "ano", "semestre", "criador", "created_at")
    search_fields = ("nome", "codigo")
    list_filter = ("ano", "semestre")


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("nome", "turma", "semestre", "criado_por", "created_at")
    search_fields = ("nome", "turma__nome")
    list_filter = ("semestre", "turma")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("titulo", "professor", "ano_escolar", "disciplina", "data")
    list_filter = ("ano_escolar", "disciplina")
    search_fields = ("titulo", "professor__user__username")


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "turma", "created_at")
    search_fields = ("aluno__user__username", "turma__nome", "turma__codigo")


@admin.register(Ano)
class AnoAdmin(admin.ModelAdmin):
    list_display = ("ano_inicio", "ano_termino")


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ("numero", "ano")
    list_filter = ("numero",)
