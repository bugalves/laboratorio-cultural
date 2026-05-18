from django.shortcuts import render
from .models import Clube, Evento, Galeria, Laboratorio, SessaoLeitura, Cidade
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login

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

    template_map = {
        'leitura': 'core/clubes/clubedeleitura.html',
        'teatro': 'core/clubes/clubedeteatro.html',
    }

    template = template_map.get(
        clube.tipo,
        'core/clubes/not-found.html'
    )

    # Se aceder a /clubes/clube-de-leitura só faz query dos livros
    if clube.tipo == 'leitura':
        # Retorna somente os 3 últimos livros a ser inseridos
        livros = clube.livro_set.all()[:3]

        return render(request, template, {
            'clube': clube,
            'livros': livros,
        })
    
    # Se aceder a /clubes/clube-de-teatro só faz query dos eventos
    if clube.tipo == 'teatro':
        eventos = clube.eventos.all()
        noticias = clube.noticias.order_by('-data_publicacao')[:3]

        return render(request, template, {
            'clube': clube,
            'eventos': eventos,
            'noticias': noticias
        })
    
    # Se não for nenhum dos dois não retorna nenhuma informação, devolve página 'not-found.html'
    return render(request, template)

def programacaocultural(request):
    return render(request, "core/programacaocultural.html")

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

def eventos_json(request):
    eventos = Evento.objects.all()
    data = []

    for evento in eventos:
        data.append({
            "title": evento.titulo,
            "start": str(evento.data_evento),
            "description": evento.descricao,
            "location": evento.local,
            "tipo": evento.tipo_evento,
            "image": evento.imagem.url,
        })

    return JsonResponse(data, safe=False)

def sessoes_leitura_json(request):
    sessoes_leitura = SessaoLeitura.objects.all()
    data = []

    for sessao in sessoes_leitura:

        if sessao.livro:

            data.append({
                'title': sessao.livro.titulo,
                'start': str(sessao.data_sessao),
                'description': sessao.livro.descricao,
                'location': sessao.local,
                'image': sessao.livro.capa.url if sessao.livro.capa else '',
            })

    return JsonResponse(data, safe=False)

from django.db.models import DateField
from django.db.models.functions import TruncDate

from itertools import chain

def programacaocultural(request):

    eventos = Evento.objects.all()
    sessoes = SessaoLeitura.objects.all()

    cidade = request.GET.get("cidade")
    tipo = request.GET.get("tipo_evento")
    data = request.GET.get("data_evento")

    # 🔥 FILTRO DATA (aplica aos dois)
    if data:
        eventos = eventos.filter(data_evento=data)
        sessoes = sessoes.filter(data_sessao=data)

    # 🔥 FILTRO TIPO (só eventos têm tipo_evento)
    if tipo:
        eventos = eventos.filter(tipo_evento=tipo)

        # opcional: se quiseres filtrar sessões também por tipo
        # podes criar lógica própria aqui depois

    # 🔥 FILTRO CIDADE (só eventos têm cidade)
    if cidade:
        eventos = eventos.filter(cidade_id=cidade)

    # ---------------- NORMALIZAÇÃO ----------------

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

    # ordenar tudo por data
    programacao = sorted(programacao, key=lambda x: x["data"] or "")

    return render(request, "core/programacaocultural.html", {
        "programacao": programacao,
        "cidades": Cidade.objects.all(),
        "tipos": Evento.objects.values_list("tipo_evento", flat=True).distinct(),
        "datas": Evento.objects.exclude(data_evento__isnull=True)
                               .values_list("data_evento", flat=True)
                               .distinct()
                               .order_by("data_evento")
    })

