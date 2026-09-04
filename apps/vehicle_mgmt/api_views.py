# -*- coding: utf-8 -*-
import io
import qrcode
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from apps.vehicle_mgmt.models import VisitorAppointment, QRPassToken
from apps.vehicle_mgmt.serializers import (
    RegisterSerializer, VisitorAppointmentSerializer, QRTokenSerializer
)


# ---- \u7528\u6237\u6ce8\u518c ----
@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username
        }, status=status.HTTP_201_CREATED)


# ---- \u9884\u7ea6 CRUD ----
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VisitorAppointment.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---- QR \u901a\u884c\u8bc1 ----
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def appointment_qr(request, pk):
    """\u751f\u6210/\u83b7\u53d6\u9884\u7ea6\u7684 QR \u901a\u884c\u8bc1\u56fe\u7247"""
    try:
        appt = VisitorAppointment.objects.get(pk=pk, user=request.user)
    except VisitorAppointment.DoesNotExist:
        return Response({"error": "\u9884\u7ea6\u4e0d\u5b58\u5728"}, status=404)

    if appt.status != "approved":
        return Response({"error": "\u9884\u7ea6\u5c1a\u672a\u901a\u8fc7\u5ba1\u6279"}, status=400)

    qr_token = QRPassToken.objects.filter(appointment=appt).first()
    if not qr_token or not qr_token.is_valid():
        if qr_token:
            qr_token.delete()
        qr_token = QRPassToken.generate_for_appointment(appt)

    qr_data = f"{request.scheme}://{request.get_host()}/api/verify-qr/{qr_token.token}/"
    img = qrcode.make(qr_data, box_size=10, border=2)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return HttpResponse(buf, content_type="image/png")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def qr_token_info(request, pk):
    """\u83b7\u53d6 QR \u4ee4\u724c\u4fe1\u606f\uff08\u6709\u6548\u671f\u7b49\uff09"""
    try:
        appt = VisitorAppointment.objects.get(pk=pk, user=request.user)
    except VisitorAppointment.DoesNotExist:
        return Response({"error": "\u9884\u7ea6\u4e0d\u5b58\u5728"}, status=404)

    qr_token = QRPassToken.objects.filter(appointment=appt).first()
    if not qr_token or not qr_token.is_valid():
        if qr_token:
            qr_token.delete()
        qr_token = QRPassToken.generate_for_appointment(appt)

    return Response({
        "token": qr_token.token,
        "expires_at": qr_token.expires_at.isoformat(),
        "is_valid": qr_token.is_valid(),
        "remaining_seconds": max(0, (qr_token.expires_at - now()).total_seconds())
    })


# ---- CSRF\u8c41\u514d\u767b\u5f55 ----
from rest_framework.authtoken.views import obtain_auth_token
csrf_exempt_login = csrf_exempt(obtain_auth_token)


# ---- \u7528\u6237\u4fe1\u606f ----
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
    })