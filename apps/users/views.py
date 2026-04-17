from django.shortcuts import render

def login(request):
    events = []
    return render(request, 'users/login.html')
