from django.shortcuts import render

def home(request):
    events = []
    return render(request, 'core/home.html', {'events': events})
