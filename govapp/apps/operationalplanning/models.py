from logging import getLogger

from django.contrib import auth
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db.models import MultiLineStringField, MultiPolygonField
from django.db import models
from django.db.models import Q
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from govapp.apps.actions.models import Action
from govapp.apps.burnplanning.models import BurnPlanElement
from govapp.apps.legalapproval.models import (
    ApprovableModel,
    AuthorityToTake,
    LegalApproval,
)
from govapp.apps.main.models import (
    AssignableModel,
    DisplayNameableModel,
    IntervalFloatField,
    IntervalIntegerField,
    ModelFile,
    ReferenceableModel,
    UniqueNameableModel,
    YearField,
)
from govapp.apps.prescriptiondetails.models import (
    PRESCRIPTION_DETAILS,
    FuelType,
    format_prescription_detail_name,
)
from govapp.apps.risk.models import (
    AdditionalControl,
    ContributingFactor,
    OverwriteControl,
    RiskCategory,
    RiskRating,
)
from govapp.apps.traffic.models import Traffic

logger = getLogger(__name__)

User = auth.get_user_model()


class OperationalPlanRiskCategory(models.Model):
    operational_plan = models.ForeignKey(
        "OperationalPlan", null=True, blank=True, on_delete=models.CASCADE
    )
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE)
    contributing_factor: models.ManyToManyField = models.ManyToManyField(
        ContributingFactor,
        related_name="risk_categories",
        editable=False,
        through="OperationalPlanRiskCategoryContributingFactor",
        through_fields=("operational_plan_risk_category", "contributing_factor"),
    )  # For each risk category one or more contributing factors can be selected

    def __str__(self) -> str:
        return f"{self.operational_plan} - {self.risk_category}"


# TODO maybe change this class to end in overwrite control OverwriteControl
class OperationalPlanRiskCategoryContributingFactorOverwriteControl(models.Model):
    class Meta:
        verbose_name = "Standard Control Overwrite"
        verbose_name_plural = "Standard Control Overwrites"
        unique_together = (
            "operational_plan_risk_category_contributing_factor",
            "overwrite_control",
        )

    operational_plan_risk_category_contributing_factor = models.ForeignKey(
        "OperationalPlanRiskCategoryContributingFactor",
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factor_control_overwrites",
    )
    overwrite_control = models.ForeignKey(
        OverwriteControl,
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factor_control_overwrites",
    )

    def clean(self):
        standard_controls = (
            self.operational_plan_risk_category_contributing_factor.contributing_factor.standard_controls.all()
        )
        if standard_controls.exists() is False:
            raise ValidationError(
                "Contributing factor has no standard controls to overwrite"
            )
        if standard_controls.contains(self.overwrite_control.standard_control) is False:
            raise ValidationError(
                "Overwrite control must be of the same types as contributing factor's standard controls"
            )
        return super().clean()


class OperationalPlanRiskCategoryContributingFactorAdditionalControl(models.Model):
    class Meta:
        verbose_name = "Additional Control"
        verbose_name_plural = "Additional Controls"
        unique_together = (
            "operational_plan_risk_category_contributing_factor",
            "additional_control",
        )

    operational_plan_risk_category_contributing_factor = models.ForeignKey(
        "OperationalPlanRiskCategoryContributingFactor",
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factor_additional_control",
    )
    additional_control = models.ForeignKey(
        AdditionalControl,
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factor_additional_control",
    )

    def __str__(self) -> str:
        return f"{self.operational_plan_risk_category_contributing_factor} - {self.additional_control}"

    def clean(self):
        contributing_factor = self.operational_plan_risk_category_contributing_factor
        if (
            not contributing_factor.standard_control_risk_level_requires_additional_controls
        ):
            risk_rating = (
                self.operational_plan_risk_category_contributing_factor.risk_rating_standard
            )
            raise ValidationError(
                f"Additional controls are not required for this standard control risk rating ({risk_rating})"
            )
        return super().clean()

    @property
    def revisit_in_implementation_plan(self):
        return self.additional_control.revisit_in_implementation_plan


class OperationalPlanRiskCategoryContributingFactor(models.Model):
    operational_plan_risk_category = models.ForeignKey(
        OperationalPlanRiskCategory, on_delete=models.CASCADE
    )
    contributing_factor = models.ForeignKey(
        ContributingFactor, on_delete=models.CASCADE
    )
    values_affected = models.TextField(null=True, blank=True)
    contributing_factor_control_overwrites: models.ManyToManyField = (
        models.ManyToManyField(
            OverwriteControl,
            related_name="operational_plan_risk_category_contributing_factors",
            editable=False,
            through="OperationalPlanRiskCategoryContributingFactorOverwriteControl",
            through_fields=(
                "operational_plan_risk_category_contributing_factor",
                "overwrite_control",
            ),
        )
    )  # In IP the standard control contributing factors can be overwritten if revisit_in_implementation_plan is set
    risk_rating_standard = models.ForeignKey(
        RiskRating,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factors_for_standard_controls",
        verbose_name="Risk rating (after application of standard controls)",
    )  # Risk rating after application of standard controls

    additional_controls: models.ManyToManyField = models.ManyToManyField(
        AdditionalControl,
        related_name="operational_plan_risk_category_contributing_factors",
        through="OperationalPlanRiskCategoryContributingFactorAdditionalControl",
        through_fields=(
            "operational_plan_risk_category_contributing_factor",
            "additional_control",
        ),
        editable=False,
    )  # Only applies if risk level of risk rating requires additional controls

    risk_ratings_additional: models.ManyToManyField = models.ManyToManyField(
        RiskRating,
        related_name="operational_plan_risk_category_contributing_factors",
        through="OperationalPlanRiskCategoryContributingFactorAdditionalControlRiskRating",
        through_fields=(
            "operational_plan_risk_category_contributing_factor",
            "risk_rating",
        ),
        editable=False,
    )  # Risk rating after application of additional controls

    def __str__(self) -> str:
        return f"{self.operational_plan_risk_category} - {self.contributing_factor}"

    @property
    def standard_control_risk_level_requires_additional_controls(self):
        if not self.risk_rating_standard:
            return False
        return self.risk_rating_standard.risk_level.requires_additional_controls


class OperationalPlanRiskCategoryContributingFactorAdditionalControlRiskRating(
    models.Model
):
    class Meta:
        verbose_name = "Risk Rating (after application of additional controls)"
        verbose_name_plural = "Risk Ratings (after application of additional controls)"

    operational_plan_risk_category_contributing_factor = models.ForeignKey(
        OperationalPlanRiskCategoryContributingFactor,
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factor_risk_ratings",
    )
    risk_rating = models.ForeignKey(
        RiskRating,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="operational_plan_risk_category_contributing_factor_risk_ratings",
    )

    def __str__(self) -> str:
        return f"{self.operational_plan_risk_category_contributing_factor} {self.risk_rating}"

    def clean(self):
        contributing_factor = self.operational_plan_risk_category_contributing_factor
        if (
            not contributing_factor.standard_control_risk_level_requires_additional_controls
        ):
            risk_rating = (
                self.operational_plan_risk_category_contributing_factor.risk_rating_standard
            )
            raise ValidationError(
                f"Additional risk ratings are not required for this standard control risk rating ({risk_rating})"
            )
        return super().clean()

    @property
    def requires_additional_controls(self):
        return self.risk_rating.risk_level.requires_additional_controls


class OperationalArea(
    ReferenceableModel, UniqueNameableModel, TimeStampedModel, ApprovableModel
):
    MODEL_PREFIX = "OA"

    burn_plan_element: models.ForeignKey = models.ForeignKey(
        BurnPlanElement,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_areas",
    )

    # GIS data
    polygon = MultiPolygonField(blank=True, null=True)
    linestring = MultiLineStringField(blank=True, null=True)
    district = models.ForeignKey(
        "main.District",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="operational_areas",
    )

    # Overview
    year = YearField(
        null=True, blank=True
    )  # Year in which the operational area is active/valid?
    operational_area_different_from_bpu_rationale = models.TextField(
        null=True, blank=True
    )
    # Contentious burn is coming from BPE Details section for operational area (not sure it belongs here or in BPE)
    contentious_burn = models.BooleanField(default=False)
    contentious_rationale = models.TextField(null=True, blank=True)

    # Legal/approvals

    @property
    def region(self):
        if self.district and self.district.region:
            return self.district.region
        return None

    @property
    def area_sqm(self):
        if not hasattr(self, "area") or not self.area:
            logger.warn(f"OperationalArea: {self.id} has no area")
            return None
        return self.area.sq_m

    @property
    def area_ha(self):
        if not hasattr(self, "area") or not self.area:
            logger.warn(f"OperationalArea: {self.id} has no area")
            return None
        return self.area.sq_m / 10000

    def initial_required_approvals(self):
        return LegalApproval.objects.filter(
            is_required_for_operational_area=True
        ).values_list("name", flat=True)

    def initial_not_required_approvals(self):
        # Automatically create entries for other additional required approvals by intersecting with Tenure layer
        # TODO: Make sure this is correct. Karsten can't remember what this is for
        return LegalApproval.objects.filter(land_type__length__gt=0).values_list(
            "name", flat=True
        )

    @property
    def all_approvals(self):
        """Returns the legal approvals from the initial_required_approvals and initial_not_required_approvals
        methods without any duplicates"""
        return (
            LegalApproval.objects.filter(
                Q(is_required_for_operational_plan=True) | Q(land_type__length__gt=0)
            )
            .distinct()
            .values_list("name", flat=True)
        )

    def copy(self):
        self.pk = None
        self.save()
        return self


class OperationalPlan(
    StatusModel,
    ReferenceableModel,
    UniqueNameableModel,
    TimeStampedModel,
    ApprovableModel,
    AssignableModel,
):
    MODEL_PREFIX = "OP"

    operationalplanpurposes: "models.Manager[OperationalPlanPurpose]"
    operationalplanprograms: "models.Manager[OperationalPlanProgram]"
    objectiveandsuccesscriteria: "models.Manager[ObjectiveAndSuccessCriteria]"

    # Define types for dynamically added managers to keep mypy happy
    draft: models.Manager
    with_district_officer: models.Manager
    with_district_officer_referral: models.Manager
    with_regional_leader_fire: models.Manager
    with_regional_leader_fire_referral: models.Manager
    with_fmsb_representative: models.Manager
    with_district_manager: models.Manager
    with_regional_manager: models.Manager
    with_state_manager: models.Manager
    approved: models.Manager

    STATUS_DRAFT = "draft"
    STATUS_WITH_DISTRICT_OFFICER = "with_district_officer"
    STATUS_WITH_DISTRICT_OFFICER_REFERRAL = "with_district_officer_referral"
    STATUS_WITH_REGIONAL_LEADER_FIRE = "with_regional_leader_fire"
    STATUS_WITH_REGIONAL_LEADER_FIRE_REFERRAL = "with_regional_leader_fire_referral"
    STATUS_WITH_FMSB_REPRESENTATIVE = "with_fmsb_representative"
    STATUS_WITH_DISTRICT_MANAGER = "with_district_manager"
    STATUS_WITH_REGIONAL_MANAGER = "with_regional_manager"
    STATUS_WITH_STATE_MANAGER = "with_state_manager"
    STATUS_APPROVED = "approved"
    STATUS_DISCARDED = "discarded"

    STATUS = Choices(
        (STATUS_DRAFT, "Draft"),
        (STATUS_WITH_DISTRICT_OFFICER, "With District Officer"),
        (STATUS_WITH_DISTRICT_OFFICER_REFERRAL, "With District Officer (Referral)"),
        (STATUS_WITH_REGIONAL_LEADER_FIRE, "With Regional Leader Fire"),
        (
            STATUS_WITH_REGIONAL_LEADER_FIRE_REFERRAL,
            "With Regional Leader Fire (Referral)",
        ),
        (STATUS_WITH_FMSB_REPRESENTATIVE, "With FMSB Representative"),
        (STATUS_WITH_DISTRICT_MANAGER, "With District Manager"),
        (STATUS_WITH_REGIONAL_MANAGER, "With Regional Manager"),
        (STATUS_WITH_STATE_MANAGER, "With State Manager"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DISCARDED, "Discarded"),
    )

    operational_area = models.ForeignKey(
        OperationalArea,
        on_delete=models.CASCADE,
        related_name="operational_plans",
    )

    # Overview
    operation_name = models.CharField(
        max_length=255, null=True, blank=True
    )  # To be copied from Details section for operational area in BPE
    purpose: models.ManyToManyField = models.ManyToManyField(
        "burnplanning.Purpose",
        related_name="operational_plans",
        through="OperationalPlanPurpose",
        through_fields=("operational_plan", "purpose"),
        editable=False,
    )  # Copied from BPE, but editable (multi-select)
    program: models.ManyToManyField = models.ManyToManyField(
        "burnplanning.Program",
        related_name="operational_plans",
        through="OperationalPlanProgram",
        through_fields=("operational_plan", "program"),
        editable=False,
    )  # Copied from BPE, but editable (multi-select)

    OPERATIONS = Choices(
        ("burning", "Burning"),
        ("mechanical", "Stand-alone Mechanical"),
    )
    operation = models.CharField(
        max_length=255,
        choices=OPERATIONS,
        null=False,
        blank=False,
        default="burning",
    )
    operational_intent = models.TextField(null=True, blank=True)

    # Priority
    burn_priority = IntervalIntegerField(
        min_value=1, max_value=10, null=True, blank=True
    )
    WINDOW_OF_OPPORTUNITY_VALUES = Choices(
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
    window_of_opportunity = models.CharField(
        max_length=255,
        choices=WINDOW_OF_OPPORTUNITY_VALUES,
        null=True,
        blank=True,
    )  # Chance of completing burn if postponed

    # Context
    context_description_of_burn = models.TextField(
        null=True, blank=True, verbose_name="Description of burn"
    )
    context_risk_of_not_completing_burn = models.TextField(
        null=True, blank=True, verbose_name="Risk of not completing burn"
    )
    context_operational_aspects = models.TextField(
        null=True, blank=True, verbose_name="Operational aspects (PESTLE)"
    )
    context_map = models.ForeignKey(ModelFile, on_delete=models.PROTECT, null=True)

    # Objectives and Success Criteria: ObjectiveAndSuccessCriteria

    # Traffic
    traffic = models.ForeignKey(
        Traffic,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="operational_plans",
    )

    # Burn Values List
    # TODO Sections, Questions, Actions

    # Risk Categories: OperationalPlanRiskCategory
    # risk_ratings

    # Contingencies
    # contingencies

    prescription = models.ForeignKey(
        "Prescription",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="operational_plans",
    )

    # Legal / Approvals
    flora_authority_to_take = models.ForeignKey(
        AuthorityToTake,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Flora Authority To Take",
        related_name="%(class)s_flora_att",
    )  # Flora authority to take
    fauna_authority_to_take = models.ForeignKey(
        AuthorityToTake,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Fauna Authority To Take",
        related_name="%(class)s_fauna_att",
    )  # Fauna authority to take

    # Actions
    actions = GenericRelation(Action)

    # Documents
    documents = GenericRelation(
        ModelFile, related_query_name="operationalplan_document"
    )

    @property
    def year(self):
        return self.operational_area.burn_plan_element.year

    @cached_property
    def districts(self):
        return list(
            self.operational_area.burn_plan_element.burn_plan_unit.districts.values_list(
                "display_name", flat=True
            )
        )

    @cached_property
    def regions(self):
        return list(
            self.operational_area.burn_plan_element.burn_plan_unit.districts.values_list(
                "region__display_name", flat=True
            )
        )

    @property
    def burn_plan_unit(self):
        return self.operational_area.burn_plan_element.burn_plan_unit.reference_number

    @property
    def assigned_to_name(self):
        return self.assigned_to.get_full_name()

    @property
    def risk_highest_level(self):
        # Highest risk level from Risk section
        raise NotImplementedError("TODO")

    @property
    def priority_calculated(self):
        # Calculated priority from Priority section
        raise NotImplementedError("TODO")

    def initial_required_approvals(self):
        return LegalApproval.objects.filter(
            is_required_for_operational_plan=True
        ).values_list("name", flat=True)

    def initial_not_required_approvals(self):
        # Automatically create entries for other additional required approvals by intersecting with Tenure layer
        # TODO: Make sure this is correct. Karsten can't remember what this is for
        return LegalApproval.objects.filter(land_type__length__gt=0).values_list(
            "name", flat=True
        )

    @property
    def all_approvals(self):
        """Returns the legal approvals from the initial_required_approvals and initial_not_required_approvals
        methods without any duplicates"""
        return (
            LegalApproval.objects.filter(
                Q(is_required_for_operational_plan=True) | Q(land_type__length__gt=0)
            )
            .distinct()
            .values_list("name", flat=True)
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def assignable_users(self):
        # TODO uncomment once which groups members are asignable
        # GROUPS = [
        #     "TODO: Add appropriate groups here",
        # ]
        # return User.objects.filter(is_active=True, groups__name__in=GROUPS).distinct()
        return User.objects.filter(is_active=True, is_staff=True)


class OperationalPlanPurpose(TimeStampedModel):
    operational_plan = models.ForeignKey(
        OperationalPlan,
        on_delete=models.CASCADE,
        related_name="operationalplanpurposes",
    )
    purpose = models.ForeignKey(
        "burnplanning.Purpose",
        on_delete=models.CASCADE,
        related_name="operationalplanpurposes",
    )


class OperationalPlanProgram(TimeStampedModel):
    operational_plan = models.ForeignKey(
        OperationalPlan,
        on_delete=models.CASCADE,
        related_name="operationalplanprograms",
    )
    program = models.ForeignKey(
        "burnplanning.Program",
        on_delete=models.CASCADE,
        related_name="operationalplanprograms",
    )


class SuccessCriteriaLeftValue(UniqueNameableModel, DisplayNameableModel):
    class Meta:
        verbose_name = "Objective and Success Criteria - Success Criterion Left Value"
        verbose_name_plural = (
            "Objective and Success Criteria - Success Criterion Left Values"
        )


class SuccessCriteriaComparisonOperator(UniqueNameableModel, DisplayNameableModel):
    class Meta:
        verbose_name = (
            "Objective and Success Criteria - Success Criterion Comparison Operator"
        )
        verbose_name_plural = (
            "Objective and Success Criteria - Success Criterion Comparison Operators"
        )


class SuccessCriteriaReport(UniqueNameableModel, DisplayNameableModel):
    class Meta:
        verbose_name = "Objective and Success Criteria - Success Criterion Report"
        verbose_name_plural = (
            "Objective and Success Criteria - Success Criterion Reports"
        )

    success_criteria = models.ForeignKey(
        "SuccessCriteria",
        on_delete=models.CASCADE,
        related_name="successcriteriareports",
        null=True,
        blank=True,
    )

    RESULTS = Choices(
        ("achieved", "Achieved"),
        ("not_achieved", "Not Achieved"),
        ("not_started", "Not Started"),
    )
    result = models.CharField(
        max_length=255,
        choices=RESULTS,
        null=True,
        blank=True,
    )
    # Allow for recording a percentage if the result is achieved or not achieved. Modeling this as a ratio [0,1]
    result_achieved_ratio = IntervalFloatField(
        min_value=0.0, max_value=1.0, null=True, blank=True
    )


class SuccessCriteria(UniqueNameableModel, DisplayNameableModel):
    class Meta:
        verbose_name = "Objective and Success Criteria - Success Criterion"
        verbose_name_plural = "Objective and Success Criteria - Success Criteria"

    objectiveandsuccesscriteria: "models.Manager[ObjectiveAndSuccessCriteria]"

    left_value = models.ForeignKey(
        SuccessCriteriaLeftValue,
        on_delete=models.CASCADE,
        related_name="successcriteria",
        null=True,
        blank=True,
    )
    comparison_operator = models.ForeignKey(
        SuccessCriteriaComparisonOperator,
        on_delete=models.CASCADE,
        related_name="successcriteria",
        null=True,
        blank=True,
    )
    right_value_or_free_text = models.TextField(null=True, blank=True)
    objective_and_success_criteria = models.ForeignKey(
        "ObjectiveAndSuccessCriteria",
        on_delete=models.CASCADE,
        related_name="success_criteria",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return (
            f"{self.objective_and_success_criteria} - {self.left_value} "
            f"{self.comparison_operator} {self.right_value_or_free_text}"
        )


class Objective(UniqueNameableModel, DisplayNameableModel):
    class Meta:
        verbose_name = "Objective and Success Criteria - Objective"
        verbose_name_plural = "Objective and Success Criteria - Objectives"

    objectiveandsuccesscriteria: "models.Manager[ObjectiveAndSuccessCriteria]"


class ObjectiveAndSuccessCriteria(TimeStampedModel):
    class Meta:
        verbose_name = "Objective and Success Criterion"
        verbose_name_plural = "Objective and Success Criteria"

    operational_plan = models.ForeignKey(
        OperationalPlan,
        on_delete=models.CASCADE,
        related_name="objectiveandsuccesscriteria",
    )
    objective = models.ForeignKey(
        Objective,
        on_delete=models.CASCADE,
        related_name="objectiveandsuccesscriteria",
    )
    details = models.TextField(null=True, blank=True)
    applicable_to_whole_operational_area = models.BooleanField(default=False)

    # Success Criteria
    # 1toMany - SuccessCriteria

    def __str__(self) -> str:
        return f"{self.operational_plan} - {self.objective}"


class ContingencyNeighbour(models.Model):
    contingency = models.ForeignKey(
        "Contingency",
        on_delete=models.CASCADE,
        related_name="contingency_neighbours",
    )
    neighbour = models.ForeignKey(
        "main.Neighbour",
        on_delete=models.CASCADE,
        related_name="contingency_neighbours",
    )

    def __str__(self) -> str:
        return f"{self.contingency} - {self.neighbour}"


class Contingency(DisplayNameableModel):
    class Meta:
        verbose_name = "Contingency"
        verbose_name_plural = "Contingencies"

    operational_plan = models.ForeignKey(
        OperationalPlan,
        on_delete=models.CASCADE,
        related_name="contingencies",
    )
    suppression_constraints = models.TextField(null=True, blank=True)
    neighbours: models.ManyToManyField = models.ManyToManyField(
        "main.Neighbour",
        related_name="contingencies",
        verbose_name="Neighbouring landowners and significant stakeholders",
        through="ContingencyNeighbour",
        through_fields=("contingency", "neighbour"),
    )

    @property
    def context_map(self):
        if not hasattr(self, "operational_plan") and not hasattr(
            self.operational_plan, "context_map"
        ):
            return "Will be filled from Context section of the Operational Plan"
        return mark_safe(
            "<a href='{}' target='blank'>{}</a>".format(
                self.operational_plan.context_map.file.url,
                self.operational_plan.context_map,
            )
        )


class PrescriptionFuelType(models.Model):
    class Meta:
        verbose_name = "Burning Prescription Fuel Type"
        verbose_name_plural = "Burning Prescription Fuel Types"
        unique_together = ("prescription", "fuel_type")

    prescription = models.ForeignKey(
        "Prescription",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
    )
    fuel_type = models.ForeignKey(
        FuelType,
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
    )
    cell_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Cell"
    )
    scorch_height = models.ForeignKey(
        "prescriptiondetails.ScorchHeight",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("scorch_height"),
    )
    burn_area = models.ForeignKey(
        "prescriptiondetails.BurnArea",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("burn_area"),
    )
    ros_range = models.ForeignKey(
        "prescriptiondetails.RosRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("ros_range"),
    )
    ffdi_range = models.ForeignKey(
        "prescriptiondetails.FfdiRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("ffdi_range"),
    )
    glc_range = models.ForeignKey(
        "prescriptiondetails.GlcRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("glc_range"),
    )
    gfdi_range = models.ForeignKey(
        "prescriptiondetails.GfdiRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("gfdi_range"),
    )
    temperature_range = models.ForeignKey(
        "prescriptiondetails.TemperatureRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("temperature_range"),
    )
    rh_range = models.ForeignKey(
        "prescriptiondetails.RhRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("rh_range"),
    )
    sdi = models.ForeignKey(
        "prescriptiondetails.Sdi",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("sdi"),
    )
    smc_range = models.ForeignKey(
        "prescriptiondetails.SmcRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("smc_range"),
    )
    pmc_range = models.ForeignKey(
        "prescriptiondetails.PmcRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("pmc_range"),
    )
    wind_speed_range = models.ForeignKey(
        "prescriptiondetails.WindSpeedRange",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("wind_speed_range"),
    )
    wind_direction = models.ForeignKey(
        "prescriptiondetails.WindDirection",
        on_delete=models.CASCADE,
        related_name="prescription_fuel_types",
        null=True,
        blank=True,
        verbose_name=format_prescription_detail_name("wind_direction"),
    )

    fuel_assessment_summary = GenericRelation(ModelFile)
    fire_behaviour_calculations = GenericRelation(ModelFile)

    def __str__(self) -> str:
        return f"{self.prescription} - {self.fuel_type}"

    @property
    def applicable_fuel_type_prescription_details(self):
        return self.fuel_type.applicable_fuel_type_prescription_details.all()

    def clean(self):
        attrs = PRESCRIPTION_DETAILS.keys()
        applicable_details = self.applicable_fuel_type_prescription_details.values_list(
            "prescription_detail", flat=True
        )
        set_details = [attr for attr in attrs if getattr(self, attr)]
        if any(detail not in applicable_details for detail in set_details):
            raise ValidationError("Invalid prescription detail for this fuel type")
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)


class Prescription(models.Model):
    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"

    operational_overview = models.TextField(null=True, blank=True)
    ignition_sequence = models.TextField(null=True, blank=True)
    fuel_types: models.ManyToManyField = models.ManyToManyField(
        FuelType,
        related_name="prescriptions",
        verbose_name="Fuel Types",
        through="PrescriptionFuelType",
        through_fields=("prescription", "fuel_type"),
    )

    def __str__(self) -> str:
        truncate_length = 40
        text = str(self.operational_overview)
        return text[:truncate_length] + ".." if len(text) > truncate_length else text
