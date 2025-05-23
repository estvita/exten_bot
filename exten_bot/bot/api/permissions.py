import os

from rest_framework.permissions import BasePermission


class AllowTrustedIpOrAuthenticated(BasePermission):
    def has_permission(self, request, view):
        trusted_ips = os.environ.get("TRUSTED_IPS", "127.0.0.1").split(",")
        ip_addr = request.META.get("HTTP_X_REAL_IP")
        if ip_addr in trusted_ips:
            return True
        return request.user and request.user.is_authenticated
