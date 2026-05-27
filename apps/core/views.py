from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from .models import (
    Clube,
    Evento,
    Galeria,
    Laboratorio,
    SessaoLeitura,
    Cidade,
    SessaoTeatro
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


# ---------------- LOGIN ----------------
def login_view(request):

    error = None

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:

            if not user.is_superuser and not email.endswith("@ispgaya.pt"):
                error = "Apenas emails @ispgaya.pt são permitidos"
                return render(request, "registration/login.html", {"error": error})

            login(request, user)

            if user.is_superuser or user.nivel in ["admin", "moderador"]:
                user.is_staff = True
                user.save()
                return redirect("/admin/")

            return redirect("/")

        else:
            error = "Credenciais inválidas"

    return render(request, "registration/login.html", {"error": error})


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
        programacao.append({
            "titulo": e.titulo,
            "descricao": e.descricao,
            "data": e.data_evento.strftime("%d/%m/%Y") if e.data_evento else "",
            "local": e.local,
            "imagem": e.imagem.url if e.imagem else "",
        })

    for s in sessoes:
        if s.livro:
            programacao.append({
                "titulo": s.livro.titulo,
                "descricao": s.livro.descricao,
                "data": s.data_sessao.strftime("%d/%m/%Y") if s.data_sessao else "",
                "local": s.local,
                "imagem": s.livro.capa.url if s.livro.capa else "",
            })

    programacao = sorted(programacao, key=lambda x: x["data"] or "")

    return render(request, "core/programacaocultural.html", {
        "programacao": programacao,
        "cidades": Cidade.objects.all(),
        "tipos": Evento.objects.values_list("tipo_evento", flat=True).distinct(),
        "datas": Evento.objects.exclude(
            data_evento__isnull=True
        ).values_list("data_evento", flat=True).distinct().order_by("data_evento"),
    })

@login_required
def participar_evento(request, tipo, evento_id):

    if request.method != "POST":
        return JsonResponse({"error": "Método inválido"}, status=400)

    if tipo == "leitura":
        obj = get_object_or_404(SessaoLeitura, id=evento_id)

    elif tipo == "teatro":
        obj = get_object_or_404(SessaoTeatro, id=evento_id)

    elif tipo == "evento":
        obj = get_object_or_404(Evento, id=evento_id)

    else:
        return JsonResponse({"error": "Tipo inválido"}, status=400)

    if request.user in obj.participantes.all():
        return JsonResponse({"error": "Já inscrito"}, status=400)

    if hasattr(obj, "lotado") and obj.lotado():
        return JsonResponse({"error": "Lotado"}, status=400)

    obj.participantes.add(request.user)

    return JsonResponse({
        "success": True,
        "inscritos": obj.participantes.count(),
        "vagas_restantes": obj.vagas - obj.participantes.count() if hasattr(obj, "vagas") else None
    })