import logging

# Third-Party
from drf_spectacular import utils
from rest_framework import viewsets

from govapp.apps.operationalplanning import serializers
from govapp.apps.operationalplanning.models import OperationalPlan

logger = logging.getLogger(__name__)


@utils.extend_schema(tags=["Operational Planning - OperationalPlans"])
class OperationalPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Operational Plan ViewSet."""

    queryset = OperationalPlan.objects.all()
    serializer_class = serializers.OperationalPlanSerializer

    def get_serializer_class(self):
        format = self.request.query_params.get("format", None)
        if self.action == "list" and format == "datatables":
            return serializers.OperationalPlanDatatableSerializer
        return self.serializer_class
