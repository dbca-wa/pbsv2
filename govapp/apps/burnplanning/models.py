from logging import getLogger

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PolygonField
from django.contrib.gis.db.models.functions import Area
from django.db import models
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.functions import Cast
from django.utils.functional import cached_property
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel

from govapp.apps.main.models import (
    ArchivableModel,
    AssignableModel,
    District,
    EndorsableModel,
    IntervalIntegerField,
    KeyValueListModelMixin,
    NameableModel,
    ReferenceableModel,
    UniqueFieldKeyValueListModelMixin,
    UniqueNameableModel,
    YearField,
)

logger = getLogger(__name__)


class BurnPlanUnitManager(models.Manager):
    def get_queryset_with_polygons(self):
        return (
            super()
            .get_queryset()
            .annotate(area=Area(Cast("polygon", PolygonField(geography=True))))
        )


class BurnPlanUnit(
    UniqueFieldKeyValueListModelMixin,
    KeyValueListModelMixin,
    DirtyFieldsMixin,
    ReferenceableModel,
    UniqueNameableModel,
    StatusModel,
    AssignableModel,
    TimeStampedModel,
):
    """A burn plan unit is a model to contain geometry information for
    an area that may be assigned to a burn plan element"""

    MODEL_PREFIX = "BPU"

    objects = BurnPlanUnitManager()

    STATUS = Choices(
        ("draft", "Draft"),
        ("current", "Current"),
        ("discarded", "Discarded"),
        ("retired", "Retired"),
    )

    # Define types for dynamically added managers to keep mypy happy
    draft: models.Manager
    current: models.Manager
    discarded: models.Manager
    retired: models.Manager

    burnplanunitdistricts: ReverseManyToOneDescriptor

    districts: models.ManyToManyField = models.ManyToManyField(
        District,
        through="BurnPlanUnitDistrict",
        through_fields=("burn_plan_unit", "district"),
        editable=False,
    )

    polygon = PolygonField(blank=True, null=True)
    active_from = YearField(null=True, blank=True)
    active_to = YearField(null=True, blank=True)
    return_interval = IntervalIntegerField(min_value=1, null=True, blank=True)
    allow_recording_of_hectares = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.reference_number} ({self.name})"

    @property
    def area_sqm(self):
        if not self.area:
            logger.warn(f"BurnPlanUnit: {self.id} has no area")
            return None
        return self.area.sq_m

    @property
    def area_sqhm(self):
        if not self.area:
            logger.warn(f"BurnPlanUnit: {self.id} has no area")
            return None
        return self.area.sq_m / 10000

    @property
    def operational_areas(self):
        return self.operationalareas.all()

    @cached_property
    def district_names(self):
        return list(self.districts.values_list("display_name", flat=True))

    @cached_property
    def regions(self):
        return list(self.districts.values_list("region__display_name", flat=True))

    def assignable_users(self):
        # TODO uncomment once groups are listed above (will probably change based on the status of the instance too)
        # GROUPS = [
        #     "TODO: Add appropriate groups here",
        # ]
        # return User.objects.filter(is_active=True, groups__name__in=GROUPS).distinct()
        return User.objects.filter(is_active=True)


class BurnPlanUnitDistrict(TimeStampedModel):
    """A model to store the relationship between a burn plan unit and a district"""

    burn_plan_unit = models.ForeignKey(
        BurnPlanUnit, on_delete=models.CASCADE, related_name="burnplanunitdistricts"
    )
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="burnplanunitdistricts"
    )
    # Todo: confirm business rules for primary district (largest land area? or other?)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Burn Plan Unit: {self.burn_plan_unit} "
            f"includes land in district: {self.district} ({self.district.region})"
        )

    class Meta:
        verbose_name_plural = "Burn Plan Unit Districts"
        unique_together = ("burn_plan_unit", "district")


class Treatment(
    KeyValueListModelMixin, UniqueNameableModel, ArchivableModel, TimeStampedModel
):
    pass


class Justification(
    KeyValueListModelMixin, UniqueNameableModel, ArchivableModel, TimeStampedModel
):
    pass


class Purpose(
    KeyValueListModelMixin, UniqueNameableModel, ArchivableModel, TimeStampedModel
):
    operationalplanpurposes: ReverseManyToOneDescriptor


class Program(
    KeyValueListModelMixin, UniqueNameableModel, ArchivableModel, TimeStampedModel
):
    operationalplanprograms: ReverseManyToOneDescriptor


class OutputLeaderType(UniqueNameableModel, ArchivableModel, TimeStampedModel):
    pass


class OutputLeader(NameableModel, ArchivableModel, TimeStampedModel):
    burn_plan_element = models.ForeignKey(
        "BurnPlanElement", on_delete=models.CASCADE, related_name="output_leaders"
    )
    type = models.ForeignKey(
        OutputLeaderType, on_delete=models.PROTECT, null=True, blank=True
    )
    indicative_treatment_year = YearField(null=True, blank=True)
    revised_indicative_treatment_year = YearField(null=True, blank=True)
    preferred_season = models.CharField(
        max_length=255, choices=settings.SEASON_CHOICES, null=True, blank=True
    )
    comments = models.TextField(null=True, blank=True)


class BurnPlanElement(
    UniqueFieldKeyValueListModelMixin,
    KeyValueListModelMixin,
    DirtyFieldsMixin,
    ReferenceableModel,
    UniqueNameableModel,
    StatusModel,
    AssignableModel,
    EndorsableModel,
    TimeStampedModel,
):
    MODEL_PREFIX = "BPE"

    STATUS = Choices(
        ("draft", "Draft"),
        ("current", "Current"),
        ("discarded", "Discarded"),
        ("retired", "Retired"),
    )

    # Define types for dynamically added managers to keep mypy happy
    draft: models.Manager
    current: models.Manager
    discarded: models.Manager
    retired: models.Manager

    burn_plan_unit = models.OneToOneField(
        to=BurnPlanUnit, on_delete=models.PROTECT, null=True, blank=True
    )
    year = YearField(null=True, blank=True)
    last_relevant_treatment_year = YearField(null=True, blank=True)
    indicative_treatment_year = YearField(null=True, blank=True)
    revised_indicative_treatment_year = YearField(null=True, blank=True)
    return_interval = IntervalIntegerField(min_value=1, null=True, blank=True)
    preferred_season = models.CharField(
        max_length=255, choices=Choices(*settings.SEASON_CHOICES), null=True, blank=True
    )
    treatment = models.ForeignKey(
        to=Treatment, on_delete=models.PROTECT, null=True, blank=True
    )
    justification = models.ForeignKey(
        to=Justification, on_delete=models.PROTECT, null=True, blank=True
    )
    purposes = models.ManyToManyField(Purpose)
    programs = models.ManyToManyField(Program)

    def __str__(self):
        return f"{self.reference_number} ({self.name})"

    def assignable_users(self):
        # TODO uncomment once groups are listed above (will probably change based on the status of the instance too)
        # GROUPS = [
        #     "TODO: Add appropriate groups here",
        # ]
        # return User.objects.filter(is_active=True, groups__name__in=GROUPS).distinct()
        return User.objects.filter(is_active=True)

    def users_able_to_endorse(self):
        # TODO uncomment once groups are listed above (will probably change based on the status of the instance too)
        # GROUPS = [
        #     "TODO: Add appropriate groups here",
        # ]
        # return User.objects.filter(is_active=True, groups__name__in=GROUPS).distinct()
        return User.objects.filter(is_active=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for output_leader_types in OutputLeaderType.objects.all():
            output_leader, created = OutputLeader.objects.get_or_create(
                type=output_leader_types, burn_plan_element=self
            )
            if created:
                logger.info(f"Created output leader: {output_leader}")

    @property
    def regions(self):
        return list({d.region for d in self.burn_plan_unit.districts.all()})

    @property
    def districts(self):
        return self.burn_plan_unit.districts.all()
