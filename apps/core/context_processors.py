from .models import Inscricao

def user_inscricoes(request):
    if not request.user.is_authenticated:
        return {"inscricoes": []}

    inscricoes = Inscricao.objects.filter(
        utilizador=request.user
    )

    inscricoes_modal = []

    for i in inscricoes:
        atividade = i.atividade

        inscricoes_modal.append({
            "id": i.id,
            "titulo": getattr(atividade, "titulo", None)
            or (
                atividade.livro.titulo
                if hasattr(atividade, "livro") and atividade.livro
                else "Sem título"
            ),
            "local": atividade.local,
            "tipo": atividade.__class__.__name__,
        })

    return {"inscricoes": inscricoes_modal}