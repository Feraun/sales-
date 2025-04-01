from django.shortcuts import render, redirect

# Create your views here.
def ind(request):
    if request.method == 'POST':
        if "sign_up" in request.POST:
            return redirect('authentication:reg')
        if "login" in request.POST:
            return redirect('authentication:login')

    return render(request, 'index.html')