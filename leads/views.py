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

        # STEP 1: CHECK BY IDEMPOTENCY KEY
        existing = Lead.objects.filter(
            idempotency_key=idempotency_key
        ).first()

        if existing:
            return Response(LeadSerializer(existing).data, status=200)

        # STEP 2: CHECK BY EMAIL (FINAL FIX)
        existing_email = Lead.objects.filter(
            email=request.data.get("email")
        ).first()

        if existing_email:
            if existing_email.idempotency_key == idempotency_key:
                return Response(LeadSerializer(existing_email).data, status=200)
            else:
                return Response(
                    {"error": "Email already exists with different request"},
                    status=400
                )
        # STEP 3: VALIDATE
        serializer = LeadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        #  STEP 4: SAVE
        try:
            lead = serializer.save(idempotency_key=idempotency_key)

        except IntegrityError:
            existing = Lead.objects.filter(
                email=request.data.get("email")
            ).first()

            if existing:
                return Response(LeadSerializer(existing).data, status=200)

            return Response(
                {"error": "Duplicate request conflict"},
                status=409
            )

        # STEP 5: ASYNC TASK
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
