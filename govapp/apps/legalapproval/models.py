from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel

from govapp.apps.main.models import (
    DisplayNameableModel,
    Lga,
    ModelFile,
    UniqueNameableModel,
)


# Let's call the class LegalApproval to not confuse with an Approval model
class LegalApproval(UniqueNameableModel, DisplayNameableModel):
    """Burn Program and Operational Area/Operational Plan approvals"""

    objects = models.Manager()

    modellegalapprovals: "models.Manager[ModelLegalApproval]"

    # TODO Not sure on this one, but requirement item #72 mentions these three separately
    APPROVAL_TYPES = Choices(
        ("endorsement", "Endorsement"),
        ("approval", "Approval"),
        ("endorsement_or_approval", "Endorsement/Approval"),
    )
    approval_type = models.CharField(
        max_length=255, choices=APPROVAL_TYPES, null=True, blank=True
    )
    # TODO There must be a better term than land_type?
    LAND_TYPE_SHIRE = "shire"
    LAND_TYPES = Choices(
        (LAND_TYPE_SHIRE, "Shire"),
        ("owner", "Owner"),
        ("other", "Other Lands"),
    )
    land_type = models.CharField(
        max_length=255, choices=LAND_TYPES, null=True, blank=True
    )  # To be added by the system after intersection

    approver: models.CharField = models.CharField(
        max_length=255, null=True, blank=True
    )  # Corporate Executive, Shire, Other Lands, Owner

    has_additional_permissions: models.BooleanField = models.BooleanField(
        default=False
    )  # Whether the user can attach files, texts, or remove the approval
    is_required_for_operational_area = models.BooleanField(default=False)
    is_required_for_operational_plan = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Legal/Approval"
        verbose_name_plural = "Legal/Approvals"

    def __str__(self) -> str:
        return f"{self.approver} {self.get_approval_type_display()}"

    @property
    def is_shire_approval(self):
        return self.land_type == self.LAND_TYPE_SHIRE

    @property
    def can_remove_approval(self):
        return self.has_additional_permissions and self.text_remove_justification


class ModelLegalApproval(TimeStampedModel):
    file_as_approval = GenericRelation(ModelFile)
    text_as_approval: models.TextField = models.TextField(null=True, blank=True)
    text_remove_justification: models.TextField = models.TextField(
        null=True, blank=True
    )

    legal_approval = models.ForeignKey(
        LegalApproval,
        on_delete=models.CASCADE,
        related_name="modellegalapprovals",
    )  # OP: endorsement and approval by district manager and regional manager

    # OP: lodgement date of DAS proposal + approval and expiry date of the issued DAS approval
    # OP: lodgement date of the related Flora and Fauna 'Authority To Take' lawful authorities
    # + issue and expiry date of the issued lawful authorities

    lga: models.ForeignKey = models.ForeignKey(
        Lga,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Shire/LGA",
        related_name="modellegalapprovals",
    )  # Shire

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="content_type"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name_plural = "Legal/Approvals"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.legal_approval} entry for "
            f"{self.content_object.__class__.__name__} {self.content_object.__str__()} "
        )

    @property
    def has_lga(self):
        if not hasattr(self, "legal_approval"):
            raise AttributeError(
                "Model needs to implement a foreign key to LegalApproval to access `has_lga`"
            )
        return self.legal_approval.has_lga

    @property
    def has_additional_permissions(self):
        if not hasattr(self, "legal_approval"):
            raise AttributeError(
                "Model needs to implement a foreign key to LegalApproval to access `has_additional_permissions`"
            )
        return self.legal_approval.has_additional_permissions

    def clean(self) -> None:
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ApprovableModel(models.Model):
    legal_approvals = GenericRelation(ModelLegalApproval)

    # Automatically create entries for other additional required approvals by intersecting with Tenure layer in CDDP
    requires_other_land_approval = models.BooleanField(default=False)
    requires_owner_approvals = models.BooleanField(
        default=False
    )  # One or more owner approvals
    requires_shire_approvals = models.BooleanField(
        default=False
    )  # One or more shire approvals

    class Meta:
        abstract = True

    def clean(self):
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def required_approvals(self):
        pass
