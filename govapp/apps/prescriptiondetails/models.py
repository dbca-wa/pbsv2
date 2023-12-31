from django.db import models
from model_utils import Choices

from govapp.apps.main.models import DetailMeta, UniqueNameableModel

"""Might need to use a model instead of a dict for this"""
PRESCRIPTION_DETAILS = {
    "scorch_height": {
        "singular": "Scorch Height",
        "plural": "Scorch Heights",
        "abbreviation": "",
    },
    "burn_area": {
        "singular": "Area to be burnt",
        "plural": "Areas to be burnt",
        "abbreviation": "",
    },
    "ros_range": {
        "singular": "Rate of Spread",
        "plural": "Rates of Spread",
        "abbreviation": "ROS",
    },
    "ffdi_range": {
        "singular": "Forest Fire Danger Index",
        "plural": "Forest Fire Danger Indices",
        "abbreviation": "FFDI",
    },
    "glc_range": {
        "singular": "Ground Level Concentration",
        "plural": "Ground Level Concentrations",
        "abbreviation": "GLC",
    },
    "gfdi_range": {
        "singular": "Grass Fire Danger Index",
        "plural": "Grass Fire Danger Indices",
        "abbreviation": "GFDI",
    },
    "temperature_range": {
        "singular": "Temperature",
        "plural": "Temperatures",
        "abbreviation": "",
    },
    "rh_range": {
        "singular": "Relative Humidity",
        "plural": "Relative Humidities",
        "abbreviation": "RH",
    },
    "sdi": {
        "singular": "Soil Dryness Index",
        "plural": "Soil Dryness Indices",
        "abbreviation": "SDI",
    },
    "smc_range": {
        "singular": "Surface Fuel Moisture Content",
        "plural": "Surface Fuel Moisture Contents",
        "abbreviation": "SMC",
    },
    "pmc_range": {
        "singular": "Profile Fuel Moisture Content",
        "plural": "Profile Fuel Moisture Contents",
        "abbreviation": "PMC",
    },
    "wind_speed_range": {
        "singular": "Wind Speed",
        "plural": "Wind Speeds",
        "abbreviation": "",
    },
    "wind_direction": {
        "singular": "Wind Direction",
        "plural": "Wind Directions",
        "abbreviation": "",
    },
}

PRESCRIPTION_DETAILS_CHOICES = (
    ("scorch_height", PRESCRIPTION_DETAILS["scorch_height"]["singular"]),
    ("burn_area", PRESCRIPTION_DETAILS["burn_area"]["singular"]),
    ("ros_range", PRESCRIPTION_DETAILS["ros_range"]["singular"]),
    ("ffdi_range", PRESCRIPTION_DETAILS["ffdi_range"]["singular"]),
    ("glc_range", PRESCRIPTION_DETAILS["glc_range"]["singular"]),
    ("gfdi_range", PRESCRIPTION_DETAILS["gfdi_range"]["singular"]),
    ("temperature_range", PRESCRIPTION_DETAILS["temperature_range"]["singular"]),
    ("rh_range", PRESCRIPTION_DETAILS["rh_range"]["singular"]),
    ("sdi", PRESCRIPTION_DETAILS["sdi"]["singular"]),
    ("smc_range", PRESCRIPTION_DETAILS["smc_range"]["singular"]),
    ("pmc_range", PRESCRIPTION_DETAILS["pmc_range"]["singular"]),
    ("wind_speed_range", PRESCRIPTION_DETAILS["wind_speed_range"]["singular"]),
    ("wind_direction", PRESCRIPTION_DETAILS["wind_direction"]["singular"]),
)


def format_prescription_detail_name(key, plural=False):
    """Format a prescription detail name based on the key and whether it is plural
    Returns a string in the form of "Singular Name (Abbreviation)" or "Plural Name (Abbreviation)"
    """

    if key not in PRESCRIPTION_DETAILS:
        raise ValueError(f"{key} is not a valid prescription detail key")
    abbreviation = PRESCRIPTION_DETAILS[key]["abbreviation"]
    abbreviation = f" ({abbreviation})" if abbreviation else ""
    if plural:
        return f"{PRESCRIPTION_DETAILS[key]['plural']}{abbreviation}"
    return f"{PRESCRIPTION_DETAILS[key]['singular']}{abbreviation}"


class PrescriptionDetailMeta(DetailMeta):
    DETAILS = PRESCRIPTION_DETAILS


class PrescriptionDetail(UniqueNameableModel, metaclass=PrescriptionDetailMeta):
    __metaclass__: PrescriptionDetailMeta

    class Meta:
        abstract = True


class ScorchHeight(PrescriptionDetail):
    detail_key = "scorch_height"


class BurnArea(PrescriptionDetail):
    detail_key = "burn_area"


class RosRange(PrescriptionDetail):
    detail_key = "ros_range"


class FfdiRange(PrescriptionDetail):
    detail_key = "ffdi_range"


class GlcRange(PrescriptionDetail):
    detail_key = "glc_range"


class GfdiRange(PrescriptionDetail):
    detail_key = "gfdi_range"


class TemperatureRange(PrescriptionDetail):
    detail_key = "temperature_range"


class RhRange(PrescriptionDetail):
    detail_key = "rh_range"


class Sdi(PrescriptionDetail):
    detail_key = "sdi"


class SmcRange(PrescriptionDetail):
    detail_key = "smc_range"


class PmcRange(PrescriptionDetail):
    detail_key = "pmc_range"


class WindSpeedRange(PrescriptionDetail):
    detail_key = "wind_speed_range"


class WindDirection(PrescriptionDetail):
    detail_key = "wind_direction"


class ApplicableFuelTypePrescriptionDetail(models.Model):
    class Meta:
        verbose_name = "Fuel Type - Applicable Prescription Detail"
        verbose_name_plural = "Fuel Type - Applicable Prescription Details"

    prescription_detail = models.CharField(
        choices=Choices(*PRESCRIPTION_DETAILS_CHOICES),
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )

    def __str__(self):
        return format_prescription_detail_name(self.prescription_detail)


class FuelType(UniqueNameableModel):
    class Meta:
        verbose_name = "Fuel Type"
        verbose_name_plural = "Fuel Types"

    # The system is to intersect the operational area with the Fuel Type layer
    # to prefill the fuel types in the Prescription section (Reqs Id 56)
    fuel_type_layer = models.CharField(max_length=255, blank=True, null=True)
    applicable_fuel_type_prescription_details = models.ManyToManyField(
        ApplicableFuelTypePrescriptionDetail, related_name="fuel_types"
    )
