import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required

from .models import (
    Utilizador,
    Clube,
    Evento,
    Galeria,
    Laboratorio,
    SessaoLeitura,
    Cidade,
    SessaoTeatro,
    Inscricao
)


# ---------------- HOME ----------------
def home(request):
    clubes = Clube.objects.all()
    eventos = Evento.objects.all()
    galerias = Galeria.objects.all()
    laboratorio = Laboratorio.objects.first()

    return render(request, 'core/home.html', {
        'clubes': clubes,
        'eventos': eventos,
        'galerias': galerias,
        'laboratorio': laboratorio,
    })


def clube_detail(request, slug):
    clube = get_object_or_404(Clube, slug=slug)

    if clube.tipo == 'leitura':
        template = 'core/clubes/clubedeleitura.html'
        return render(request, template, {
            'clube': clube,
            'livros': clube.livros.all()[:3],
            'sessoes': SessaoLeitura.objects.filter(livro__clube=clube),
        })

    elif clube.tipo == 'teatro':
        template = 'core/clubes/clubedeteatro.html'
        return render(request, template, {
            'clube': clube,
            'eventos': Evento.objects.all(),
            'sessoes': SessaoTeatro.objects.all(),
            'noticias': clube.noticias.order_by('-data_publicacao')[:3],
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
            "vagas": s.vagas,
            "inscritos": s.inscritos(),
            "lotado": s.lotado(),
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
            "vagas": e.vagas,
            "inscritos": e.inscritos(),
            "lotado": e.lotado(),
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
            "vagas": s.vagas,
            "inscritos": s.inscritos(),
            "lotado": s.lotado(),
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
            "vagas": e.vagas,
            "inscritos": e.inscritos(),
            "lotado": e.lotado(),
            "tipo": "evento",
            "color": "#2e7d32",
        })

    return JsonResponse(data, safe=False)

# ---------------- AUTH ----------------
def login_view(request):
    error = None
    next_url = request.GET.get("next")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

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

    return render(
        request,
        "registration/login.html",
        {
            "error": error,
            "next": next_url
        }
    )


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

# ---------------- PROGRAMAÇÃO CULTURAL ----------------
def programacaocultural(request):
    eventos = Evento.objects.all()
    sessoes = SessaoLeitura.objects.all()

    cidade = request.GET.get("cidade")
    tipo = request.GET.get("tipo_evento")
    data = request.GET.get("data_evento")

    if data:
        eventos = eventos.filter(data_evento=data)
        sessoes = sessoes.filter(data_sessao=data)

    if tipo:
        eventos = eventos.filter(tipo_evento=tipo)

    if cidade:
        eventos = eventos.filter(cidade_id=cidade)

    programacao = []

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

    for s in sessoes:
        if s.livro:
            ja_inscrito = False

            if request.user.is_authenticated:
                ja_inscrito = Inscricao.objects.filter(
                    utilizador=request.user,
                    sessao_leitura=s
                ).exists()

            programacao.append({
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

    programacao = sorted(programacao, key=lambda x: x["data"] or "")

    inscricoes_modal = []

    if request.user.is_authenticated:
        inscricoes = (
            Inscricao.objects
            .filter(utilizador=request.user)
            .select_related(
                "evento",
                "sessao_leitura",
                "sessao_teatro"
            )
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
                    if hasattr(atividade, "livro")
                    and atividade.livro
                    else "Sem título"
                ),
                "local": atividade.local,
                "tipo": atividade.__class__.__name__,
            })

    return render(request, "core/programacaocultural.html", {
        "programacao": programacao,
        "inscricoes": inscricoes_modal,
        "cidades": Cidade.objects.all(),
        "tipos": Evento.objects.values_list("tipo_evento", flat=True).distinct(),
        "datas": Evento.objects.exclude(
            data_evento__isnull=True
        ).values_list("data_evento", flat=True).distinct().order_by("data_evento"),
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
