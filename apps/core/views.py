import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import (
    Utilizador,
    Clube,
    Evento,
    Galeria,
    SessaoLeitura,
    Cidade,
    SessaoTeatro,
    Inscricao,
    Livro,
    Noticia
)


# ---------------- HOME ----------------
def home(request):
    clubes = Clube.objects.all()
    eventos = Evento.objects.all()

    return render(request, 'core/home.html', {
        'clubes': clubes,
        'eventos': eventos,
    })

@login_required
@require_POST
def participar(request, tipo, id):

    modelos = {
        "evento": Evento,
        "leitura": SessaoLeitura,
        "teatro": SessaoTeatro,
    }

    model = modelos.get(tipo)
    if not model:
        return JsonResponse({"error": "Tipo inválido"}, status=400)

    objeto = get_object_or_404(model, pk=id)

    if objeto.lotado:
        return JsonResponse({"error": "Sem vagas"}, status=400)

    filtros = {"utilizador": request.user}

    if tipo == "evento":
        filtros["evento"] = objeto
    elif tipo == "leitura":
        filtros["sessao_leitura"] = objeto
    elif tipo == "teatro":
        filtros["sessao_teatro"] = objeto

    inscricao, created = Inscricao.objects.get_or_create(**filtros)

    if not created:
        return JsonResponse({
            "success": False,
            "already": True,
            "message": "Já estás inscrito nesta atividade."
        })

    return JsonResponse({
        "success": True,
        "created": True,
        "vagas_restantes": objeto.vagas_restantes,
        "inscritos": objeto.inscritos
    })

def clube_detail(request, slug):
    clube = get_object_or_404(Clube, slug=slug)

    if clube.tipo == 'leitura':
        livros = Livro.objects.filter(clube_id=1)
        print("DEBUG LIVROS:", list(livros))

        return render(request, 'core/clubes/clubedeleitura.html', {
            'clube': clube,
            'livros': livros,
            'sessoes': SessaoLeitura.objects.all(),
        })

    elif clube.tipo == 'teatro':
        noticias = Noticia.objects.filter(clube_id=2)

        return render(request, 'core/clubes/clubedeteatro.html', {
            'clube': clube,
            'noticias': noticias,
            'sessoes': SessaoTeatro.objects.all(),
            'galerias': Galeria.objects.all(),
        })


    return render(request, 'core/clubes/not-found.html', {
        'clube': clube
    })

def calendario_teatro_json(request, slug):
    sessoes = SessaoTeatro.objects.all()
    eventos = Evento.objects.all()

    data = []

    for s in sessoes:
        if not s.data_sessao:
            continue

        data.append({
            "id": s.id,
            "title": s.titulo,
            "start": s.data_sessao.isoformat(),
            "description": s.descricao or "",
            "local": s.local or "",
            "cidade": s.cidade.nome if s.cidade else "",
            "vagas_restantes": s.vagas_restantes,
            "inscritos": s.inscritos,
            "lotado": s.lotado,
            "tipo": "teatro",
            "color": "#c62828",
        })

    for e in eventos:
        if not e.data_evento:
            continue

        data.append({
            "id": e.id,
            "title": e.titulo,
            "start": e.data_evento.isoformat(),
            "description": e.descricao or "",
            "local": e.local or "",
            "cidade": e.cidade.nome if e.cidade else "",
            "vagas_restantes": e.vagas_restantes,
            "inscritos": e.inscritos,
            "lotado": e.lotado,
            "tipo": "evento",
            "color": "#2e7d32",
        })

    return JsonResponse(data, safe=False)


def calendario_leitura_json(request, slug):
    sessoes = SessaoLeitura.objects.all()
    eventos = Evento.objects.all()

    data = []

    for s in sessoes:
        if not s.data_sessao:
            continue

        data.append({
            "id": s.id,
            "title": s.livro.titulo if s.livro else "Sessão Leitura",
            "start": s.data_sessao.isoformat(),
            "description": s.livro.descricao if s.livro else "",
            "local": s.local or "",
            "cidade": s.cidade.nome if s.cidade else "",
            "vagas_restantes": s.vagas_restantes,
            "inscritos": s.inscritos,
            "lotado": s.lotado,
            "tipo": "leitura",
            "color": "#1565c0",
        })

    for e in eventos:
        if not e.data_evento:
            continue

        data.append({
            "id": e.id,
            "title": e.titulo,
            "start": e.data_evento.isoformat(),
            "description": e.descricao or "",
            "local": e.local or "",
            "cidade": e.cidade.nome if e.cidade else "",
            "vagas_restantes": e.vagas_restantes,
            "inscritos": e.inscritos,
            "lotado": e.lotado,
            "tipo": "evento",
            "color": "#2e7d32",
        })

    return JsonResponse(data, safe=False)

# ---------------- AUTH ----------------
def login_view(request):
    error = None
    next_url = request.GET.get("next") or request.POST.get("next")

    if next_url in [None, "", "None", "null"]:
        next_url = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # ADMIN
            if user.is_superuser or user.nivel in ["admin", "moderador"]:
                user.is_staff = True
                user.save()
                return redirect("/admin/")
            
            if next_url:
                return redirect(next_url)
            return redirect("/")

        else:
            error = "Credenciais inválidas"

    return render(request, "registration/login.html", {
        "error": error,
        "next": next_url or ""
    })


def register_view(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        
        if not email or not password:
            error = "Preenche todos os campos"
        elif password != password_confirm:
            error = "As passwords não coincidem"
        elif Utilizador.objects.filter(email=email).exists():
            error = "Este email já está registado"
        else:
            user = Utilizador.objects.create_user(
                email=email,
                password=password
            )

            # Login após registo
            user = authenticate(
                request,
                username=email,
                password=password
            )

            if user:
                login(request, user)
                return redirect("/")
            return redirect("/")

    return render(
        request,
        "registration/register.html",
        {"error": error}
    )


@login_required
def update_user(request):
    if request.method != "PUT":
        return JsonResponse(
            {"error": "Método não permitido"},
            status=405
        )

    data = json.loads(
        request.body.decode("utf-8")
    )

    email = data.get("email")
    password = data.get("password")
    user = request.user

    if email:
        user.email = email

    if password:
        user.set_password(password)

    user.save()

    update_session_auth_hash(
        request,
        user
    )

    return JsonResponse({
        "success": True
    })


def logout_view(request):
    logout(request)
    return redirect("/")

def programacaocultural(request):
    eventos = Evento.objects.all()
    sessoes = SessaoLeitura.objects.all()
    sessoes_teatro = SessaoTeatro.objects.all()

    cidade = request.GET.get("cidade")
    tipo = request.GET.get("tipo_atividade")
    date_range = request.GET.get("date_range")

    dates = None

    date_range = request.GET.get("date_range")

    dates = None

    if date_range:
        if " até " in date_range:
            dates = date_range.split(" até ")
        elif " to " in date_range:
            dates = date_range.split(" to ")
        else:
            dates = [date_range]

    if dates and len(dates) == 2:
        data_inicio, data_fim = dates

        eventos = eventos.filter(data_evento__range=[data_inicio, data_fim])
        sessoes = sessoes.filter(data_sessao__range=[data_inicio, data_fim])
        sessoes_teatro = sessoes_teatro.filter(data_sessao__range=[data_inicio, data_fim])

    elif dates and len(dates) == 1:
        data_unica = dates[0]

        eventos = eventos.filter(data_evento=data_unica)
        sessoes = sessoes.filter(data_sessao=data_unica)
        sessoes_teatro = sessoes_teatro.filter(data_sessao=data_unica)

    # ---------------- FILTRO CIDADE ----------------
    if cidade:
        eventos = eventos.filter(cidade_id=cidade)
        sessoes = sessoes.filter(cidade_id=cidade)
        sessoes_teatro = sessoes_teatro.filter(cidade_id=cidade)

    # ---------------- FILTRO TIPO ----------------
    if tipo == "evento":
        sessoes = SessaoLeitura.objects.none()
        sessoes_teatro = SessaoTeatro.objects.none()

    elif tipo == "leitura":
        eventos = Evento.objects.none()
        sessoes_teatro = SessaoTeatro.objects.none()

    elif tipo == "teatro":
        eventos = Evento.objects.none()
        sessoes = SessaoLeitura.objects.none()

    # ---------------- BUILD PROGRAMACAO ----------------
    programacao = []

    # EVENTOS
    for e in eventos:
        ja_inscrito = False

        if request.user.is_authenticated:
            ja_inscrito = Inscricao.objects.filter(
                utilizador=request.user,
                evento=e
            ).exists()

        programacao.append({
            "id": e.id,
            "titulo": e.titulo,
            "descricao": e.descricao,
            "data": e.data_evento.strftime("%d/%m/%Y") if e.data_evento else "",
            "local": e.local,
            "imagem": e.imagem.url if e.imagem else "",
            "vagas": e.vagas,
            "inscritos": e.inscritos,
            "ja_inscrito": ja_inscrito,
            "type": "evento",
            "type_label": "Evento",
        })

    # LEITURA
    for s in sessoes:
        if not s.livro:
            continue

        ja_inscrito = False

        if request.user.is_authenticated:
            ja_inscrito = Inscricao.objects.filter(
                utilizador=request.user,
                sessao_leitura=s
            ).exists()

        programacao.append({
            "id": s.id,
            "titulo": s.livro.titulo,
            "descricao": s.livro.descricao,
            "data": s.data_sessao.strftime("%d/%m/%Y") if s.data_sessao else "",
            "local": s.local,
            "imagem": s.livro.capa.url if s.livro.capa else "",
            "vagas": s.vagas,
            "inscritos": s.inscritos,
            "ja_inscrito": ja_inscrito,
            "type": "sessao_leitura",
            "type_label": "Sessão de Leitura",
        })

    # TEATRO (CORRIGIDO)
    for t in sessoes_teatro:
        if not t.data_sessao:
            continue

        ja_inscrito = False

        if request.user.is_authenticated:
            ja_inscrito = Inscricao.objects.filter(
                utilizador=request.user,
                sessao_teatro=t
            ).exists()

        programacao.append({
            "id": t.id,
            "titulo": t.titulo,
            "descricao": t.descricao,
            "data": t.data_sessao.strftime("%d/%m/%Y"),
            "local": t.local,
            "imagem": t.imagem.url if t.imagem else "",
            "vagas": t.vagas,
            "inscritos": t.inscritos,
            "ja_inscrito": ja_inscrito,
            "type": "sessao_teatro",
            "type_label": "Sessão de Teatro",
        })

    # ---------------- ORDENAR DATA ----------------
    from datetime import datetime

    programacao = sorted(
        programacao,
        key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y") if x["data"] else datetime.min
    )

    # ---------------- INSCRIÇÕES MODAL ----------------
    inscricoes_modal = []

    if request.user.is_authenticated:
        inscricoes = Inscricao.objects.filter(
            utilizador=request.user
        ).select_related(
            "evento",
            "sessao_leitura",
            "sessao_teatro"
        )

        for i in inscricoes:
            atividade = i.atividade

            inscricoes_modal.append({
                "id": i.id,
                "titulo": getattr(
                    atividade,
                    "titulo",
                    None
                ) or (
                    atividade.livro.titulo
                    if hasattr(atividade, "livro") and atividade.livro
                    else "Sem título"
                ),
                "local": atividade.local,
                "tipo": atividade.__class__.__name__,
            })

    return render(request,  "core/programacaocultural.html", {
        "programacao": programacao,
        "inscricoes": inscricoes_modal,
        "cidades": Cidade.objects.all(),
    })



@login_required
def inscrever(request):
    data = json.loads(request.body)
    tipo = data.get("tipo")
    objeto_id = data.get("id")

    modelos = {
        "evento": Evento,
        "sessao_leitura": SessaoLeitura,
        "sessao_teatro": SessaoTeatro,
    }

    model = modelos.get(tipo)

    if not model:
        return JsonResponse(
            {"error": "Tipo inválido"},
            status=400
        )

    objeto = get_object_or_404(
        model,
        pk=objeto_id
    )

    if objeto.lotado:
        return JsonResponse(
            {"error": "Sem vagas"},
            status=400
        )

    filtros = {
        "utilizador": request.user
    }

    if tipo == "evento":
        filtros["evento"] = objeto
    elif tipo == "sessao_leitura":
        filtros["sessao_leitura"] = objeto
    else:
        filtros["sessao_teatro"] = objeto

    inscricao, created = Inscricao.objects.get_or_create(
        **filtros
    )

    return JsonResponse({
        "success": True,
        "created": created
    })

def evento_detail(request, id):
    from django.http import JsonResponse
    from .models import Evento

    evento = Evento.objects.get(id=id)

    return JsonResponse({
        "id": evento.id,
        "vagas_restantes": evento.vagas_restantes,
        "inscritos": evento.inscritos,
    })


@login_required
def cancelar_inscricao(request, inscricao_id):
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Método não permitido"},
            status=405
        )

    try:
        inscricao = Inscricao.objects.get(
            id=inscricao_id,
            utilizador=request.user
        )
    except Inscricao.DoesNotExist:
        return JsonResponse(
            {"error": "Inscrição não encontrada"},
            status=404
        )

    inscricao.delete()

    return JsonResponse({
        "success": True
    })
