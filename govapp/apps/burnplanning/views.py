# from django.shortcuts import render
from rest_framework import viewsets

from govapp.apps.burnplanning import serializers
from govapp.apps.main.mixins import ChoicesKeyValueListMixin
from govapp.apps.main.models import District, Region
from govapp.apps.main.views import KeyValueListMixin

from .filters import BurnPlanElementFilter, BurnPlanUnitFilter
from .models import (
    BurnPlanElement,
    BurnPlanUnit,
    Justification,
    Program,
    Purpose,
    Treatment,
)
from .serializers import (
    BurnPlanElementSerializer,
    BurnPlanUnitSerializer,
    IndicativeTreatmentYearSerializer,
    ProgramSerializer,
    PurposeSerializer,
    RevisedIndicativeTreatmentYearSerializer,
    TreatmentSerializer,
)


class BurnPlanElementViewSet(viewsets.ModelViewSet):
    queryset = BurnPlanElement.objects.all()
    serializer_class = BurnPlanElementSerializer
    filterset_class = BurnPlanElementFilter

    class Meta:
        datatables_extra_json = ("get_options",)

    def get_options(self):
        return "options", {
            "indicative_treatment_year": BurnPlanElement.cached_unique_field_key_value_list(
                "indicative_treatment_year"
            ),
            "revised_indicative_treatment_year": BurnPlanElement.cached_unique_field_key_value_list(
                "revised_indicative_treatment_year"
            ),
            "region": Region.cached_key_value_list(),
            "district": District.cached_key_value_list(),
            "purpose": Purpose.cached_key_value_list(),
            "program": Program.cached_key_value_list(),
            "treatment": Treatment.cached_key_value_list(),
            "status": [
                {"key": x[0], "value": x[1]} for x in BurnPlanElement.STATUS._doubles
            ],
            "season": [
                {"key": x[0], "value": x[1]}
                for x in BurnPlanElement.preferred_season.field.choices
            ],
            "justification": Justification.cached_key_value_list(),
        }


class BurnPlanUnitViewSet(viewsets.ModelViewSet):
    queryset = BurnPlanUnit.objects.all()
    serializer_class = BurnPlanUnitSerializer
    filterset_class = BurnPlanUnitFilter

    class Meta:
        datatables_extra_json = ("get_options",)

    def get_serializer_class(self):
        format = self.request.query_params.get("format", None)
        if self.action == "list" and format == "datatables":
            return serializers.BurnPlanUnitDatatableSerializer
        return self.serializer_class

    def get_options(self):
        return "options", {
            "active_from": BurnPlanUnit.cached_unique_field_key_value_list(
                "active_from"
            ),
            "active_to": BurnPlanUnit.cached_unique_field_key_value_list("active_to"),
            "return_interval": BurnPlanUnit.cached_unique_field_key_value_list(
                "return_interval"
            ),
            "region": Region.cached_key_value_list(),
            "district": District.cached_key_value_list(),
            "status": [
                {"key": x[0], "value": x[1]} for x in BurnPlanUnit.STATUS._doubles
            ],
        }


class TreatmentViewSet(KeyValueListMixin, viewsets.GenericViewSet):
    """Treatment viewset"""

    queryset = Treatment.objects.all()
    serializer_class = TreatmentSerializer


class PurposeViewSet(KeyValueListMixin, viewsets.GenericViewSet):
    """Purpose viewset"""

    queryset = Purpose.objects.all()
    serializer_class = PurposeSerializer


class ProgramViewSet(KeyValueListMixin, viewsets.GenericViewSet):
    """Program viewset"""

    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class StatusViewSet(ChoicesKeyValueListMixin, viewsets.GenericViewSet):
    """Status viewset"""

    queryset = BurnPlanElement.objects.none()
    choices_dict = BurnPlanElement.STATUS._display_map


class IndicativeTreatmentYearViewSet(KeyValueListMixin, BurnPlanElementViewSet):
    """Indicative Treatment Year viewset"""

    key_value_display_field = "indicative_treatment_year"
    key_value_serializer_class = IndicativeTreatmentYearSerializer


class RevisedIndicativeTreatmentYearViewSet(KeyValueListMixin, BurnPlanElementViewSet):
    """Revised Indicative Treatment Year viewset"""

    key_value_display_field = "revised_indicative_treatment_year"
    key_value_serializer_class = RevisedIndicativeTreatmentYearSerializer
