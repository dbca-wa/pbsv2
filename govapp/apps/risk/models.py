from logging import getLogger

from django.contrib.postgres.fields import DecimalRangeField
from django.db import models
from model_utils.models import TimeStampedModel

from govapp.apps.main.models import OrdinalScaleModel, UniqueNameableModel

logger = getLogger(__name__)


class Control(UniqueNameableModel, TimeStampedModel):
    class Meta:
        abstract = True


class RevisitInImplementationPlan(TimeStampedModel):
    class Meta:
        abstract = True

    revisit_in_implementation_plan = models.BooleanField(
        default=False
    )  # Whether control can be revisited in Implementation Plan


class StandardControl(Control):
    """Control that can be configured in the admin panel"""

    contributing_factor_standard_controls: (
        "models.Manager[ContributingFactorStandardControl]"
    )

    class Meta:
        verbose_name = "Control (Standard)"
        verbose_name_plural = "Controls (Standard)"


class OverwriteControl(Control):
    """Control to overwrite the default value of a standard control"""

    class Meta:
        verbose_name = "Control (Overwrite)"
        verbose_name_plural = "Controls (Overwrite)"

    standard_control = models.ForeignKey(
        "StandardControl",
        on_delete=models.PROTECT,
        related_name="overwrite_controls",
    )

    def __str__(self):
        return f"{self.name} (overwrites {self.standard_control.name})"


class AdditionalControl(Control, RevisitInImplementationPlan):
    """Control that is only available when the resulting risk level of a risk assessment
    is configured as 'additional controls required'"""

    text = models.TextField(blank=True, null=True)  # Free text

    class Meta:
        verbose_name = "Control (Additional)"
        verbose_name_plural = "Controls (Additional)"

    def __str__(self):
        return self.text


class ContributingFactorStandardControl(RevisitInImplementationPlan):
    class Meta:
        unique_together = ("contributing_factor", "standard_control")
        verbose_name = "Standard Control Default Value"
        verbose_name_plural = "Standard Control Default Values"

    contributing_factor = models.ForeignKey(
        "ContributingFactor",
        on_delete=models.PROTECT,
        related_name="contributing_factor_standard_controls",
    )
    standard_control = models.ForeignKey(
        "StandardControl",
        on_delete=models.PROTECT,
        related_name="contributing_factor_standard_controls",
    )


class ContributingFactor(UniqueNameableModel, TimeStampedModel):
    contributing_factor_standard_controls: (
        "models.Manager[ContributingFactorStandardControl]"
    )

    factors = DecimalRangeField(default_bounds="[)", blank=True, null=True)  # type: ignore
    standard_controls: models.ManyToManyField = models.ManyToManyField(
        StandardControl,
        related_name="contributing_factors",
        through="ContributingFactorStandardControl",
        through_fields=("contributing_factor", "standard_control"),
    )


class RiskCategory(UniqueNameableModel, TimeStampedModel):
    class Meta:
        verbose_name = "Risk Category"
        verbose_name_plural = "Risk Categories"


class Consequence(UniqueNameableModel):
    pass


class Likelihood(OrdinalScaleModel):
    pass


class RiskLevel(OrdinalScaleModel):
    requires_additional_controls = models.BooleanField(default=False)


class LikelihoodOfConsequence(models.Model):
    consequence = models.ForeignKey(
        Consequence,
        on_delete=models.PROTECT,
        related_name="likelihood_of_consequence",
    )
    likelihood = models.ForeignKey(
        Likelihood,
        on_delete=models.PROTECT,
        related_name="likelihood_of_consequence",
    )
    risk_level = models.ForeignKey(
        RiskLevel,
        on_delete=models.PROTECT,
        related_name="likelihood_of_consequence",
    )

    class Meta:
        unique_together = ("consequence", "likelihood")

    def __str__(self):
        return f"'{self.consequence.name} ({self.likelihood.name})' risk: {self.risk_level})"


class RiskRating(models.Model):
    likelihood_of_consequence = models.ForeignKey(
        LikelihoodOfConsequence,
        on_delete=models.PROTECT,
        related_name="risk_rating",
        null=True,
        blank=True,
    )

    @property
    def risk_level(self):
        if not self.likelihood_of_consequence:
            return None
        return self.likelihood_of_consequence.risk_level

    def __str__(self):
        return self.likelihood_of_consequence.__str__()
