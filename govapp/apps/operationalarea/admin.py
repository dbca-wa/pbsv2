from django import forms
from django.contrib import admin

from govapp.apps.main.admin import DeleteRestrictedAdmin

from .models import (
    LegalApproval,
    OperationalArea,
    OperationalAreaApproval,
    OperationalAreaRiskFactor,
)


class LegalApprovalAdminForm(forms.ModelForm):
    class Meta:
        model = LegalApproval
        fields = "__all__"
        help_texts = {
            "has_additional_permissions": "Check to allow the user to attach a file as approval, "
            "provide free text as approval, or remove the required approval."
        }


@admin.register(LegalApproval)
class LegalApprovalAdmin(admin.ModelAdmin):
    model = LegalApproval
    form = LegalApprovalAdminForm

    list_display = (
        "approver",
        "approval_type",
        "lga",
        "has_additional_permissions",
    )

    fieldsets = (
        (
            "General information",
            {
                "fields": (
                    (
                        "approver",
                        "approval_type",
                        "lga",
                        "has_additional_permissions",
                    )
                ),
            },
        ),
    )


class OperationalAreaRiskFactorInline(admin.TabularInline):
    model = OperationalAreaRiskFactor
    extra = 0


class SelectWithOptionAttribute(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        # This allows using strings labels as usual
        if isinstance(label, dict):
            opt_attrs = label.copy()
            label = opt_attrs.pop("label")
        else:
            opt_attrs = {}
        option_dict = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )
        for key, val in opt_attrs.items():
            option_dict["attrs"][key] = val
        return option_dict


class OperationalAreaApprovalChoiceField(forms.ModelChoiceField):
    widget = SelectWithOptionAttribute

    def label_from_instance(self, obj):
        return {
            "label": super().label_from_instance(obj),
            "data-has-additional-permissions": str(obj.has_additional_permissions),
        }


class OperationalAreaApprovalAdminForm(forms.ModelForm):
    legal_approval = OperationalAreaApprovalChoiceField(
        queryset=LegalApproval.objects.all()
    )

    class Meta:
        model = OperationalAreaApproval
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data


class OperationalAreaApprovalInline(admin.StackedInline):
    model = OperationalAreaApproval
    extra = 0
    verbose_name = "Operational Area Approval"
    verbose_name_plural = "Operational Area Approvals"

    form = OperationalAreaApprovalAdminForm

    class Media:
        js = (
            "admin/js/jquery.init.js",
            "admin/class_media/js/document_load.js",
            "admin/class_media/js/operational_area_approval_admin.js",
        )

    class Meta:
        pass

    list_display = (
        "legal_approval",
        "file_as_approval",
        "has_additional_permissions",
        "text_as_approval",
        "text_remove_justification",
    )

    fieldsets = (
        (
            "Legal/Approval",
            {
                "fields": (("legal_approval",)),
                "classes": ("legal-approval",),
            },
        ),
        (
            "Additional information",
            {
                "fields": (
                    (
                        "file_as_approval",
                        "text_as_approval",
                        "text_remove_justification",
                    )
                ),
                "classes": ("additional-information", "hidden"),
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        form = super().get_formset(request, obj, **kwargs)

        return form


@admin.register(OperationalArea)
class OperationalAreaAdmin(DeleteRestrictedAdmin):
    model = OperationalArea
    list_display = (
        # "name",
        "operation_name",
    )

    inlines = [OperationalAreaApprovalInline, OperationalAreaRiskFactorInline]