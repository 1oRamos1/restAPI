import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from google.oauth2 import id_token
from google.auth.transport import requests

from dj_rest_auth.views import PasswordResetView, UserDetailsView

from ..models import Profile
from ..serializers import CustomUserDetailsSerializer

logger = logging.getLogger(__name__)


class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not User.objects.filter(email=email).exists():
            return Response({"error": "Email not registered."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)


class CustomUserDetailsView(UserDetailsView):
    serializer_class = CustomUserDetailsSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def set_csrf_cookie(request):
    return Response({'csrfToken': get_token(request)})


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    user = authenticate(request, username=data.get("username"), password=data.get("password"))
    if user:
        login(request, user)
        return JsonResponse({"message": "Logged in"})
    return JsonResponse({"error": "Invalid credentials"}, status=403)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    response = Response({"message": "Logged out successfully"}, status=200)
    response.delete_cookie('sessionid')
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    data = request.data
    username = data.get("username")
    email = data.get("email", "").strip()
    password1 = data.get("password1")
    password2 = data.get("password2")

    if not username or not email or not password1 or not password2:
        return JsonResponse({"error": "All fields are required"}, status=400)
    if password1 != password2:
        return JsonResponse({"error": "Passwords do not match"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already in use"}, status=400)

    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password1)
    )
    login(request, user)
    return JsonResponse({"message": "User created successfully"}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            credential = (
                request.data.get('credential')
                or request.data.get('id_token')
                or request.data.get('access_token')
            )
            if not credential:
                return Response({'error': 'No credential provided'}, status=400)

            idinfo = id_token.verify_oauth2_token(
                credential,
                requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID,
            )

            email = idinfo['email']
            name = idinfo.get('name', '')
            first_name = name.split()[0] if name else ''

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={'username': email, 'first_name': first_name}
            )
            login(request, user)
            return Response({'success': True, 'user': user.username})

        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return Response({'error': str(e)}, status=400)


def verify_paypal_order(order_id):
    try:
        response = requests.post(
            "https://api-m.sandbox.paypal.com/v1/oauth2/token",
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            data={"grant_type": "client_credentials"}
        )
        print("PayPal token response:", response.status_code, response.text)
        token = response.json()["access_token"]

        order_response = requests.get(
            f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("PayPal order response:", order_response.status_code, order_response.text)
        order = order_response.json()
        return order.get("status") == "COMPLETED"
    except Exception as e:
        print("PayPal error:", str(e))
        return False


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_to_pro(request):
    order_id = request.data.get("paypal_order_id")

    if not order_id:
        return Response({'error': 'Missing order ID'}, status=400)

    if not verify_paypal_order(order_id):
        return Response({'error': 'Payment not verified'}, status=400)

    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.is_pro = True
    profile.save()
    return Response({'status': 'upgraded to pro'})
