from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    """
    Endpoint pour vérifier l'état de santé de l'API
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'MyCoach API is running successfully',
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)