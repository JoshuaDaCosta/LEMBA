# 📚 Lemba App

Sistema de gestão escolar desenvolvido com Django e Django REST Framework, com suporte a aplicação web e futura aplicação mobile (KivyMD).

---

## 🚀 Objetivo

O Lemba App tem como objetivo facilitar a gestão escolar, permitindo a organização de:

- Turmas
- Disciplinas
- Materiais de estudo
- Inscrições de alunos
- Acesso diferenciado por tipo de utilizador (aluno, professor, diretor)

---

## 🧠 Funcionalidades principais

### 👤 Autenticação
- Login e registo de utilizadores
- Perfis: aluno, professor e diretor

### 🏫 Gestão escolar
- Criação de anos letivos
- Criação de semestres
- Criação de turmas
- Criação de disciplinas

### 📚 Materiais
- Upload de ficheiros por professores
- Visualização de materiais pelos alunos da turma
- Suporte a diferentes tipos de ficheiro (PDF, imagem, texto)

### 🔐 Regras de acesso
- Alunos só acedem a materiais das suas turmas
- Professores criam e gerem conteúdos
- Diretores têm acesso global

---

## ⚙️ Tecnologias usadas

- Python
- Django
- Django REST Framework (API)
- SQLite (ou outro banco de dados)
- KivyMD (futuro app mobile)
- HTML/CSS (templates atuais)

---

## 🏗️ Arquitetura

```text
Frontend (Django Templates / Futuro KivyMD App)
        ↓
Django REST API
        ↓
Database (Models: Turma, Disciplina, Material, etc.)
