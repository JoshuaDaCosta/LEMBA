import mimetypes

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Ano, Disciplina, Inscricao, Material, Perfil, Semestre, Turma


def _is_diretor(user):
    return user.is_authenticated and user.perfil.tipo == "diretor"


def home(request):
    if request.user.is_authenticated:
        tipo = request.user.perfil.tipo
        if tipo == "professor":
            return redirect("pagina_professor")
        if tipo == "aluno":
            return redirect("pagina_aluno")
    return render(request, "lemba_app/home.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(
                request,
                "lemba_app/login.html",
                {"erro": "Utilizador ou palavra-passe invalidos."},
            )

        login(request, user)

        tipo = user.perfil.tipo
        if tipo == "professor":
            return redirect("pagina_professor")
        if tipo == "aluno":
            return redirect("pagina_aluno")
        return redirect("home")

    return render(request, "lemba_app/login.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        tipo = request.POST.get("tipo", "").strip()

        if (
            not username
            or not password
            or tipo not in {"diretor", "professor", "aluno"}
        ):
            return render(
                request,
                "lemba_app/signup.html",
                {"erro": "Preencha todos os campos corretamente."},
            )

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "lemba_app/signup.html",
                {"erro": "Este nome de utilizador ja existe."},
            )

        user = User.objects.create_user(username=username, password=password)
        Perfil.objects.create(user=user, tipo=tipo)

        return redirect("login")

    return render(request, "lemba_app/signup.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def pagina_professor(request):
    if request.user.perfil.tipo not in ["professor", "diretor"]:
        return HttpResponse("Acesso negado")

    turmas = (
        Turma.objects.filter(criador=request.user.perfil)
        .select_related("ano", "semestre")
        .order_by("-created_at")
    )
    materiais = (
        Material.objects.filter(professor=request.user.perfil)
        .select_related("ano_escolar", "disciplina", "disciplina__turma", "disciplina__semestre")
        .order_by("-data")
    )
    anos = (
        Ano.objects.prefetch_related(
            "semestres",
            "turmas",
            "semestres__turmas",
            "semestres__disciplinas",
            "semestres__disciplinas__turma",
            "semestres__disciplinas__materiais",
        )
        .order_by("-ano_inicio")
    )

    context = {
        "turmas": turmas,
        "materiais": materiais,
        "anos": anos,
    }
    return render(request, "lemba_app/pagina_professor.html", context)


@login_required
def pagina_aluno(request):
    if request.user.perfil.tipo != "aluno":
        return HttpResponse("Acesso negado")

    inscricoes = (
        Inscricao.objects.filter(aluno=request.user.perfil)
        .select_related("turma")
        .order_by("-created_at")
    )
    turmas = [inscricao.turma for inscricao in inscricoes]
    materiais = (
        Material.objects.filter(disciplina__turma__in=turmas)
        .select_related(
            "ano_escolar",
            "disciplina",
            "disciplina__semestre",
            "disciplina__turma",
            "professor",
        )
        .order_by(
            "ano_escolar__ano_inicio",
            "disciplina__semestre__numero",
            "disciplina__nome",
            "-data",
        )
    )

    context = {
        "inscricoes": inscricoes,
        "materiais": materiais,
    }
    return render(request, "lemba_app/pagina_aluno.html", context)


@login_required
def upload_material(request):
    if request.user.perfil.tipo not in ["professor", "diretor"]:
        return HttpResponse("Acesso negado")

    anos = Ano.objects.all().order_by("-ano_inicio")
    disciplinas = Disciplina.objects.select_related("turma", "semestre").order_by(
        "turma__nome", "nome"
    )

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        ficheiro = request.FILES.get("ficheiro")
        ano_escolar_id = request.POST.get("ano_escolar")
        disciplina_id = request.POST.get("disciplina")

        if not titulo or not ficheiro or not ano_escolar_id or not disciplina_id:
            return render(
                request,
                "lemba_app/upload.html",
                {
                    "anos": anos,
                    "disciplinas": disciplinas,
                    "erro": "Preencha o titulo, selecione o ficheiro, o ano escolar e a disciplina.",
                },
            )

        try:
            ano_escolar = Ano.objects.get(pk=ano_escolar_id)
        except Ano.DoesNotExist:
            return render(
                request,
                "lemba_app/upload.html",
                {"anos": anos, "disciplinas": disciplinas, "erro": "Ano escolar invalido."},
            )

        try:
            disciplina = Disciplina.objects.select_related("turma", "semestre").get(
                pk=disciplina_id
            )
        except Disciplina.DoesNotExist:
            return render(
                request,
                "lemba_app/upload.html",
                {"anos": anos, "disciplinas": disciplinas, "erro": "Disciplina invalida."},
            )

        Material.objects.create(
            titulo=titulo,
            ficheiro=ficheiro,
            professor=request.user.perfil,
            ano_escolar=ano_escolar,
            disciplina=disciplina,
        )

        return redirect("pagina_professor")

    return render(
        request, "lemba_app/upload.html", {"anos": anos, "disciplinas": disciplinas}
    )


@login_required
def visualizar_material(request, material_id):
    material = get_object_or_404(
        Material.objects.select_related(
            "ano_escolar",
            "disciplina",
            "disciplina__semestre",
            "disciplina__turma",
            "professor",
        ),
        pk=material_id,
    )

    perfil = request.user.perfil
    if perfil.tipo == "aluno":
        inscrito = Inscricao.objects.filter(
            aluno=perfil, turma=material.disciplina.turma
        ).exists()
        if not inscrito:
            return HttpResponse("Acesso negado")
    elif perfil.tipo not in ["professor", "diretor"]:
        return HttpResponse("Acesso negado")

    ficheiro_nome = material.ficheiro.name.lower()
    mime_type, _ = mimetypes.guess_type(material.ficheiro.name)
    file_kind = "other"

    if mime_type:
        if mime_type.startswith("image/"):
            file_kind = "image"
        elif mime_type == "application/pdf":
            file_kind = "pdf"
        elif mime_type.startswith("text/"):
            file_kind = "text"

    if ficheiro_nome.endswith((".txt", ".md", ".py", ".json", ".csv")):
        file_kind = "text"

    text_content = None
    if file_kind == "text":
        try:
            material.ficheiro.open("r")
            text_content = material.ficheiro.read()
        except UnicodeDecodeError:
            file_kind = "other"
        finally:
            try:
                material.ficheiro.close()
            except Exception:
                pass

    context = {
        "material": material,
        "file_kind": file_kind,
        "text_content": text_content,
    }
    return render(request, "lemba_app/visualizar_material.html", context)


@login_required
def criar_turma(request):
    if request.user.perfil.tipo not in ["diretor", "professor"]:
        return HttpResponse("So professores e diretores podem criar turmas.")

    anos = Ano.objects.all().order_by("-ano_inicio")

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        codigo = request.POST.get("codigo", "").strip().upper()
        ano_id = request.POST.get("ano")
        semestre_id = request.POST.get("semestre")

        if not nome or not ano_id or not semestre_id:
            return render(
                request,
                "lemba_app/criar_turma.html",
                {"erro": "Nome, ano e semestre sao obrigatorios.", "anos": anos},
            )

        try:
            ano = Ano.objects.get(pk=ano_id)
            semestre = ano.semestres.get(pk=semestre_id)
        except (Ano.DoesNotExist, Exception):
            return render(
                request,
                "lemba_app/criar_turma.html",
                {"erro": "Ano ou semestre invalido.", "anos": anos},
            )

        turma = Turma(
            nome=nome,
            criador=request.user.perfil,
            ano=ano,
            semestre=semestre,
        )
        if codigo:
            turma.codigo = codigo

        try:
            turma.save()
        except Exception:
            return render(
                request,
                "lemba_app/criar_turma.html",
                {
                    "erro": "Nao foi possivel criar a turma. Verifique o codigo.",
                    "anos": anos,
                },
            )

        return redirect("pagina_professor")

    return render(request, "lemba_app/criar_turma.html", {"anos": anos})


@login_required
def criar_ano(request):
    if not _is_diretor(request.user):
        return HttpResponse("So o diretor pode criar anos letivos.")

    if request.method == "POST":
        ano_inicio = request.POST.get("ano_inicio")
        ano_termino = request.POST.get("ano_termino")

        if not ano_inicio or not ano_termino:
            return render(
                request,
                "lemba_app/criar_ano.html",
                {"erro": "Preencha a data de inicio e a data de termino."},
            )

        Ano.objects.create(ano_inicio=ano_inicio, ano_termino=ano_termino)
        return redirect("pagina_professor")

    return render(request, "lemba_app/criar_ano.html")


@login_required
def criar_semestre(request):
    if not _is_diretor(request.user):
        return HttpResponse("So o diretor pode criar semestres.")

    anos = Ano.objects.all().order_by("-ano_inicio")

    if request.method == "POST":
        numero = request.POST.get("numero")
        ano_id = request.POST.get("ano")

        if not numero or not ano_id:
            return render(
                request,
                "lemba_app/criar_semestre.html",
                {"erro": "Seleciona o ano e o numero do semestre.", "anos": anos},
            )

        try:
            ano = Ano.objects.get(pk=ano_id)
        except Ano.DoesNotExist:
            return render(
                request,
                "lemba_app/criar_semestre.html",
                {"erro": "Ano invalido.", "anos": anos},
            )

        try:
            Semestre.objects.create(numero=numero, ano=ano)
        except Exception:
            return render(
                request,
                "lemba_app/criar_semestre.html",
                {"erro": "Nao foi possivel criar o semestre.", "anos": anos},
            )
        return redirect("pagina_professor")

    return render(request, "lemba_app/criar_semestre.html", {"anos": anos})


@login_required
def criar_disciplina(request):
    if not _is_diretor(request.user):
        return HttpResponse("So o diretor pode criar disciplinas.")

    turmas = Turma.objects.select_related("ano", "semestre").order_by("nome")
    semestres = Semestre.objects.select_related("ano").order_by(
        "-ano__ano_inicio", "numero"
    )

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        turma_id = request.POST.get("turma")
        semestre_id = request.POST.get("semestre")

        if not nome or not turma_id or not semestre_id:
            return render(
                request,
                "lemba_app/criar_disciplina.html",
                {
                    "erro": "Nome, turma e semestre sao obrigatorios.",
                    "turmas": turmas,
                    "semestres": semestres,
                },
            )

        try:
            turma = Turma.objects.get(pk=turma_id)
            semestre = Semestre.objects.get(pk=semestre_id)
        except (Turma.DoesNotExist, Semestre.DoesNotExist):
            return render(
                request,
                "lemba_app/criar_disciplina.html",
                {
                    "erro": "Turma ou semestre invalidos.",
                    "turmas": turmas,
                    "semestres": semestres,
                },
            )

        Disciplina.objects.create(
            nome=nome,
            turma=turma,
            semestre=semestre,
            criado_por=request.user.perfil,
        )
        return redirect("pagina_professor")

    return render(
        request,
        "lemba_app/criar_disciplina.html",
        {"turmas": turmas, "semestres": semestres},
    )


@login_required
def entrar_turma(request):
    if request.user.perfil.tipo != "aluno":
        return HttpResponse("So alunos podem entrar em turmas.")

    inscricao_existente = Inscricao.objects.filter(aluno=request.user.perfil).first()

    if request.method == "POST":
        if inscricao_existente is not None:
            return render(
                request,
                "lemba_app/entrar_turma.html",
                {
                    "erro": "Ja estas inscrito numa turma.",
                    "inscricao_existente": inscricao_existente,
                },
            )

        codigo = request.POST.get("codigo", "").strip().upper()

        if not codigo:
            return render(
                request,
                "lemba_app/entrar_turma.html",
                {"erro": "Introduza um codigo valido."},
            )

        try:
            turma = Turma.objects.get(codigo=codigo)
        except Turma.DoesNotExist:
            return render(
                request,
                "lemba_app/entrar_turma.html",
                {"erro": "Turma nao encontrada."},
            )

        Inscricao.objects.create(aluno=request.user.perfil, turma=turma)
        return redirect("pagina_aluno")

    context = {
        "inscricao_existente": inscricao_existente,
    }
    return render(request, "lemba_app/entrar_turma.html", context)
