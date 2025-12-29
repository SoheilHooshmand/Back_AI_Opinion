from dj_rest_auth.views import LoginView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from django.urls import reverse
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import JWTLoginResponseSerializer, JWTLoginRequestSerializer


@extend_schema(
    methods=['POST'],
    summary="Custom JWT Login",
    description="Login and receive JWT access & refresh tokens along with user info.",
    request=JWTLoginRequestSerializer,
    responses={
        200: OpenApiResponse(
            description="JWT token with user info",
            response=JWTLoginResponseSerializer
        ),
        401: OpenApiResponse(description="Invalid credentials")
    }
)
class CustomJWTLoginView(LoginView):
    def get_response(self):
        user = self.user
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "pk": user.pk,
                "email": user.email,
                "username": user.username,
            }
        }, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name="dispatch")
class SignupAPIView(APIView):
    """
    API endpoint: create user + send confirmation email
    and return the confirmation URL in JSON.
    """

    authentication_classes = []  # Allow unauthenticated
    permission_classes = []      # Anyone can call

    def post(self, request):
        # Expect JSON body: {"username": "...", "email": "...", "password1": "...", "password2": "..."}
        data = request.data

        form = SignupForm(data)

        if not form.is_valid():
            # Return form errors as JSON
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user using allauth logic
        user = form.save(request)

        # Ensure EmailAddress exists for this user
        email = user.email
        email_address, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={"verified": False, "primary": True},
        )

        # Send confirmation and get the confirmation object
        confirmation = email_address.send_confirmation(request)
        key = confirmation.key

        # Build confirmation URL (same as in the console email)
        confirm_path = reverse("account_confirm_email", args=[key])
        confirmation_url = request.build_absolute_uri(confirm_path)

        # Finish the allauth signup flow (handles redirect/auth logic)
        complete_signup(
            request,
            user,
            app_settings.EMAIL_VERIFICATION,
            success_url=None,  # not used for API
        )

        return Response(
            {
                "detail": "Verification e-mail sent.",
                "confirmation_url": confirmation_url,
            },
            status=status.HTTP_201_CREATED,
        )