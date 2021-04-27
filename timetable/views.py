from django.shortcuts import render
from django.http import HttpResponse
from .exscript import ttmaker

# Create your views here.

def TimeTableView(request):
    year = request.GET["year"]
    batchgrp = request.GET["batchgrp"]
    batchnum_s = request.GET["batchnum"]
    try:
        batchnum = int(batchnum_s)
    except e:
        response = HttpResponse('')
        response.status_code = 69
        return response
    tt = ttmaker(year, batchgrp, batchnum)
    return HttpResponse(tt, content_type='application/json')


