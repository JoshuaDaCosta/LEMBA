from django.db import models
from django.contrib.auth.models import User
import uuid


# 👤 PERFIL (papéis do sistema)
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=10,
        choices=[
            ("diretor", "Diretor"),
            ("professor", "Professor"),
            ("aluno", "Aluno"),
        ],
    )

    def __str__(self):
        if self.user_id:
            username = User.objects.filter(pk=self.user_id).values_list(
                "username", flat=True
            ).first()
            if username:
                return f"{username} - {self.tipo}"
        return f"Perfil sem utilizador - {self.tipo}"


# 🏫 TURMA (núcleo do sistema)
class Turma(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=8, unique=True)
    ano = models.ForeignKey("Ano", on_delete=models.CASCADE, related_name="turmas")
    semestre = models.ForeignKey(
        "Semestre", on_delete=models.CASCADE, related_name="turmas"
    )
    criador = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


# 🎓 DISCIPLINA (pertence à turma)
class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    turma = models.ForeignKey(
        Turma, on_delete=models.CASCADE, related_name="disciplinas"
    )
    semestre = models.ForeignKey(
        "Semestre", on_delete=models.CASCADE, related_name="disciplinas"
    )
    criado_por = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.turma.nome})"


# 📚 MATERIAL (conteúdo do professor)
class Material(models.Model):
    titulo = models.CharField(max_length=100)
    ficheiro = models.FileField(upload_to="materiais/")
    data = models.DateTimeField(auto_now_add=True)
    ano_escolar = models.ForeignKey("Ano", on_delete=models.CASCADE)
    disciplina = models.ForeignKey(
        "Disciplina", on_delete=models.CASCADE, related_name="materiais"
    )

    professor = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name="materiais",
        limit_choices_to={"tipo": "professor"},
    )

    def __str__(self):
        return self.titulo


# inscricao pertence a turma ou seja o aluno vai se increver na turma
class Inscricao(models.Model):
    aluno = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, limit_choices_to={"tipo": "aluno"}
    )
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("aluno", "turma")

    def __str__(self):
        return f"{self.aluno} -> {self.turma}"


class Ano(models.Model):
    ano_inicio = models.DateField(null=False, blank=False)
    ano_termino = models.DateField(null=False, blank=False)

    def __str__(self):
        return f"{self.ano_inicio.year}/{self.ano_termino.year}"


class Semestre(models.Model):
    numero = models.PositiveSmallIntegerField(
        choices=[
            (1, "1 Semestre"),
            (2, "2 Semestre"),
        ]
    )
    ano = models.ForeignKey(Ano, on_delete=models.CASCADE, related_name="semestres")

    class Meta:
        unique_together = ("numero", "ano")

    def __str__(self):
        return f"{self.numero} Semestre - {self.ano}"
