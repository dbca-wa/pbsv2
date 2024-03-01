# from django.shortcuts import render
from rest_framework import viewsets

from govapp.apps.burnplanning import serializers
from govapp.apps.main.mixins import ChoicesKeyValueListMixin
from govapp.apps.main.models import District, Region
from govapp.apps.main.views import KeyValueListMixin

from .filters import BurnPlanElementFilter
from .models import BurnPlanElement, BurnPlanUnit, Program, Purpose, Treatment
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
            "status": BurnPlanElement.STATUS._display_map,
        }


class BurnPlanUnitViewSet(viewsets.ModelViewSet):
    queryset = BurnPlanUnit.objects.all()
    serializer_class = BurnPlanUnitSerializer

    def get_serializer_class(self):
        format = self.request.query_params.get("format", None)
        if self.action == "list" and format == "datatables":
            return serializers.BurnPlanUnitDatatableSerializer
        return self.serializer_class


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
