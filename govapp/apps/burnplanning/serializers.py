from rest_framework import serializers

from govapp.apps.main.serializers import GenericKeyValueSerializer

from .models import BurnPlanElement, Program, Purpose, Treatment


class PurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purpose
        fields = "__all__"


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"


class BurnPlanElementSerializer(serializers.ModelSerializer):
    region = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    treatment = serializers.CharField(source="treatment.name", read_only=True)
    purposes = PurposeSerializer(many=True, read_only=True)
    programs = ProgramSerializer(many=True, read_only=True)

    class Meta:
        model = BurnPlanElement
        fields = "__all__"

    def get_region(self, obj):
        return obj.regions

    def get_district(self, obj):
        return obj.districts


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = "__all__"


class BurnPlanElementKeyValueModelSerializer(
    serializers.ModelSerializer,
    GenericKeyValueSerializer[serializers.ModelSerializer, BurnPlanElement],
):
    class Meta(GenericKeyValueSerializer.Meta):
        model = BurnPlanElement


class IndicativeTreatmentYearSerializer(BurnPlanElementKeyValueModelSerializer):
    key = serializers.IntegerField(source="indicative_treatment_year")
    value = serializers.IntegerField(source="indicative_treatment_year")


class RevisedIndicativeTreatmentYearSerializer(BurnPlanElementKeyValueModelSerializer):
    key = serializers.IntegerField(source="revised_indicative_treatment_year")
    value = serializers.IntegerField(source="revised_indicative_treatment_year")
