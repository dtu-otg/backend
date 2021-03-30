from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.permissions import BasePermission, SAFE_METHODS


class Forbidden(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = {
        'status' : "FAILED",
        'error':'Authentication credentials were not provided'
    }

class ForbiddenHosting(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        'status' : "FAILED",
        'error':'You do not have hosting priveleges'
    }

class ForbiddenAdmin(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = {
        'status' : "FAILED",
        'error':'Only Admins can access this page'
    }

class ForbiddenActivation(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = {
        'status' : "FAILED",
        'error': 'Official DTU Email has not been verified'
    }


class AuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user or request.user.is_authenticated or request.method in SAFE_METHODS:
            return True
        else:
            raise Forbidden
    


class AuthenticatedAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        else:
            raise ForbiddenAdmin

class Hosting(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.can_host:
                return True
            else:
                raise ForbiddenHosting
        else :
            raise Forbidden

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class Authenticated(permissions.BasePermission):

    def has_permission(self,request,view):
        if not request.user or not request.user.is_authenticated:
            raise Forbidden
        else :
            return True

class AuthenticatedActivated(permissions.BasePermission):

    def has_permission(self,request,view):
        if request.user and request.user.is_authenticated:
            if request.user.is_verified:
                return True
            else:
                raise ForbiddenActivation
        else :
            raise Forbidden