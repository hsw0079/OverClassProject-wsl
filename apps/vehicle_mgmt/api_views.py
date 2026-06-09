import io
import qrcode
from django.http import HttpResponse
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


# ---- 用户注册 ----
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


# ---- 预约 CRUD ----
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VisitorAppointment.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---- QR 通行证 ----
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def appointment_qr(request, pk):
    """生成/获取预约的 QR 通行证图片"""
    try:
        appt = VisitorAppointment.objects.get(pk=pk, user=request.user)
    except VisitorAppointment.DoesNotExist:
        return Response({'error': '预约不存在'}, status=404)

    if appt.status != 'approved':
        return Response({'error': '预约尚未通过审批'}, status=400)

    # 检查是否已有有效 token
    qr_token = QRPassToken.objects.filter(appointment=appt).first()
    if not qr_token or not qr_token.is_valid():
        if qr_token:
            qr_token.delete()
        qr_token = QRPassToken.generate_for_appointment(appt)

    # 生成二维码图片
    qr_data = f"{request.scheme}://{request.get_host()}/api/verify-qr/{qr_token.token}/"
    img = qrcode.make(qr_data, box_size=10, border=2)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return HttpResponse(buf, content_type='image/png')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def qr_token_info(request, pk):
    """获取 QR 令牌信息（有效期等）"""
    try:
        appt = VisitorAppointment.objects.get(pk=pk, user=request.user)
    except VisitorAppointment.DoesNotExist:
        return Response({'error': '预约不存在'}, status=404)

    qr_token = QRPassToken.objects.filter(appointment=appt).first()
    if not qr_token:
        return Response({'error': '暂无通行证'}, status=404)

    return Response({
        'token': qr_token.token,
        'expires_at': qr_token.expires_at.isoformat(),
        'is_valid': qr_token.is_valid(),
        'remaining_seconds': max(0, (qr_token.expires_at - now()).total_seconds())
    })


# ---- 用户信息 ----
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
    })