import os
from rest_framework.permissions import BasePermission

class IsOwnerOrTrustedIp(BasePermission):
    """
    If the IP is trusted — access to all bots.
    If by token (or user) — access only to owned bots.
    Superuser has access to all bots.
    """
    def has_permission(self, request, view):
        self.trusted_ip = False
        if request.user and request.user.is_superuser:
            return True
        trusted_ips = os.environ.get("TRUSTED_IPS", "127.0.0.1").split(",")
        ip_addr = request.META.get("HTTP_X_REAL_IP")
        if ip_addr in trusted_ips:
            self.trusted_ip = True
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if getattr(self, 'trusted_ip', False):
            return True
        if request.user and request.user.is_superuser:
            return True
        return obj.owner_id == getattr(request.user, "id", None)