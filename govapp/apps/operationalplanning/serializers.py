# Third-Party
from rest_framework import serializers

from govapp.apps.main.serializers import ContentTypeSerializerMixin
from govapp.apps.operationalplanning.models import OperationalPlan


class OperationalPlanSerializer(
    ContentTypeSerializerMixin, serializers.ModelSerializer
):
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = OperationalPlan
        fields = "__all__"


class OperationalPlanDatatableSerializer(serializers.ModelSerializer):
    year = serializers.CharField()
    districts = serializers.ReadOnlyField()
    regions = serializers.ReadOnlyField()
    assigned_to_name = serializers.ReadOnlyField(allow_null=True)
    status_display = serializers.CharField(source="get_status_display")

    class Meta:
        model = OperationalPlan
        fields = [
            "id",
            "name",
            "burn_plan_unit",
            "year",
            "regions",
            "districts",
            "status",
            "status_display",
            "assigned_to_name",
        ]
