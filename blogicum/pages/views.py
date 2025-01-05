from django.shortcuts import render


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')


def error403(request, exception):
    return render(request, 'pages/403.html', status=403)

def error404(request, exception):
    return render(request, 'pages/404.html', status=404)

def error500(request):
    return render(request, 'pages/500.html', status=500)