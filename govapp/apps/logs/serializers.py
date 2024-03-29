from rest_framework import serializers

# Local
from govapp.apps.logs import models


class CommunicationsLogDocumentSerializer(serializers.ModelSerializer):
    """Communications Log Document Model Serializer."""

    class Meta:
        """Communications Log Document Model Serializer Metadata."""

        model = models.CommunicationsLogDocument
        fields = (
            "id",
            "name",
            "description",
            "uploaded_at",
            "file",
        )
        read_only_fields = ("uploaded_at",)


class CommunicationsLogEntrySerializer(serializers.ModelSerializer):
    """Communications Log Entry Model Serializer."""

    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M")
    type = serializers.CharField(source="get_type_display")
    documents = CommunicationsLogDocumentSerializer(many=True, read_only=True)
    vars()["from"] = serializers.CharField(
        source="fromm"
    )  # Work-around to use reserved keywords in serializer
    # username = serializers.CharField(source="user.username")

    class Meta:
        """Communications Log Entry Model Serializer Metadata."""

        model = models.CommunicationsLogEntry
        fields = (
            "id",
            "created_at",
            "type",
            "to",
            "cc",
            "from",
            "subject",
            "text",
            "documents",
            "username",
        )
        read_only_fields = (
            "created_at",
            "documents",
            "username",
        )


class CommunicationsLogCreateEntrySerializer(serializers.ModelSerializer):
    """Communications Log Entry Model Serializer."""

    user: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    documents = CommunicationsLogDocumentSerializer(many=True, read_only=True)

    class Meta:
        """Communications Log Entry Model Serializer Metadata."""

        model = models.CommunicationsLogEntry
        fields = (
            "id",
            "content_type",
            "object_id",
            "type",
            "to",
            "cc",
            "fromm",
            "subject",
            "text",
            "documents",
            "user",
        )


class ActionsLogEntrySerializer(serializers.ModelSerializer):
    """Actions Log Entry Model Serializer."""

    when = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    class Meta:
        """Actions Log Entry Model Serializer Metadata."""

        model = models.ActionsLogEntry
        fields = (
            "id",
            "username",
            "when",
            "what",
        )
