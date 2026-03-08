from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .tasks import enrich_lead_task
from .models import Lead
from .serializers import LeadSerializer

class LeadCreateAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {"error": "Idempotency-Key header required"},
                status=400
            )

        # FIRST: check idempotency key
        existing = Lead.objects.filter(idempotency_key=idempotency_key).first()

        if existing:
            return Response(
                LeadSerializer(existing).data,
                status=200
            )

        # THEN validate serializer
        serializer = LeadSerializer(data=request.data)

        if serializer.is_valid():
            lead = serializer.save(idempotency_key=idempotency_key)

            enrich_lead_task.delay(lead.id)

            return Response(
                LeadSerializer(lead).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)