# from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json 

@csrf_exempt
def index(request):

    # print(request.POST.get('some', 'XXXX'))
    # print(request.POST.__getitem__('some'))
    
    print(request.method)

    # test = list(request.POST.values())
    print(type(request.body.decode('utf-8')))
    # value = request.POST.get('some')
    # print(value)

    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return JsonResponse({'foo':'bar'})