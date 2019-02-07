from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'blank-page.html', { 'nav_active': 'blank' })
    # return HttpResponse('<strong>Yo mama!</strong>')