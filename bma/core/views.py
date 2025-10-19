from django.shortcuts import render

from rest_framework import viewsets

LOGIN_TEMPLATE = ""

class LoginViewSet(viewsets.ViewSet):
    
    def get(request, *args, **kwargs):

        return 