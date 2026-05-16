from django.shortcuts import render
from .models import Clube, Evento, Galeria, Laboratorio, SessaoLeitura
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
        livros = clube.livros.all()[:3]

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
        data.append({
            'title': sessao.livro.titulo,
            'start': str(sessao.data_sessao),
            'description': sessao.livro.descricao,
            'location': sessao.local,
            'image': sessao.livro.capa.url,
        })

    return JsonResponse(data, safe=False)
