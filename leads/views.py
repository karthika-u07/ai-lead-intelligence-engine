from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction,IntegrityError
from django.http import HttpResponse
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from .tasks import enrich_lead_task
from .models import Lead
from .serializers import LeadSerializer

def home(request):
    return HttpResponse("AI Lead Intelligence Engine running on AWS 🚀 CI/CD working")
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

        #  Step 1: Validate request data FIRST
        serializer = LeadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        #  Step 2: Try saving (handles race condition)
        try:
            lead = serializer.save(idempotency_key=idempotency_key)

        except IntegrityError:
            existing = Lead.objects.filter(
                idempotency_key=idempotency_key
            ).first()

            if existing:
                return Response(LeadSerializer(existing).data, status=200)

            # fallback (very rare)
            return Response(
                {"error": "Duplicate request conflict"},
                status=409)

        # Step 3: Async processing
        enrich_lead_task.delay(lead.id)

        return Response(
                LeadSerializer(lead).data,
                status=status.HTTP_201_CREATED
            )

class LeadDetailAPIView(RetrieveAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

        #  GET ALL LEADS
class LeadListAPIView(ListAPIView):
    queryset = Lead.objects.all().order_by("-id")
    serializer_class = LeadSerializer
    permission_classes = [AllowAny]
