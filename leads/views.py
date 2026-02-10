from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import enrich_lead_task
from .models import Lead
from .serializers import LeadSerializer


class LeadCreateAPIView(APIView):

    def post(self, request):

        serializer = LeadSerializer(data=request.data)

        if serializer.is_valid():
            lead = serializer.save()
            enrich_lead_task.delay(lead.id)

            return Response(
                LeadSerializer(lead).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
