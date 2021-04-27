from django.shortcuts import render
from django.http import HttpResponse
from .exscript import ttmaker
from rest_framework.generics import GenericAPIView 
from rest_framework.response import Response
from rest_framework import status, permissions
from user.permissions import Authenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.

year_param = openapi.Parameter('year', openapi.IN_QUERY, description="year for time table e.g. 2k19", type=openapi.TYPE_STRING)
batchgrp_param = openapi.Parameter('batchgrp', openapi.IN_QUERY, description="batch group time table e.g. A / B", type=openapi.TYPE_STRING)
batchnum_param = openapi.Parameter('batchnum', openapi.IN_QUERY, description="batch number for time table e.g 1, 2, 3, etc", type=openapi.TYPE_INTEGER)

class TimeTableView(GenericAPIView):
    # permission_classes = [Authenticated]

    @swagger_auto_schema(operation_description="get timetable", manual_parameters=[year_param, batchgrp_param, batchnum_param])
    def get(self, request):
        year = request.GET["year"]
        batchgrp = request.GET["batchgrp"]
        batchnum_s = request.GET["batchnum"]
        try:
            batchnum = int(batchnum_s)
        except e:
            response = HttpResponse('')
            response.status_code = 69
            return response
        tt = ttmaker(year, batchgrp, batchnum, True)
        return Response(tt, status=status.HTTP_200_OK)






