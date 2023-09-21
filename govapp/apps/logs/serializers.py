
# Third-Party
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
        read_only_fields = (
            "uploaded_at",
        )


class CommunicationsLogEntrySerializer(serializers.ModelSerializer):
    """Communications Log Entry Model Serializer."""
    documents = CommunicationsLogDocumentSerializer(many=True, read_only=True)
    vars()["from"] = serializers.CharField(source="fromm")  # Work-around to use reserved keywords in serializer
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
            "username"
        )
        read_only_fields = (
            "created_at",
            "documents",
            "username",
        )

class CommunicationsLogCreateEntrySerializer(serializers.ModelSerializer):
    """Communications Log Entry Model Serializer."""
    documents = CommunicationsLogDocumentSerializer(many=True, read_only=True)
    vars()["from"] = serializers.CharField(source="fromm")  # Work-around to use reserved keywords in serializer

    class Meta:
        """Communications Log Entry Model Serializer Metadata."""
        model = CommunicationsLogEntrySerializer.Meta.model
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
            "user",
        )

class ActionsLogEntrySerializer(serializers.ModelSerializer):
    """Actions Log Entry Model Serializer."""
    class Meta:
        """Actions Log Entry Model Serializer Metadata."""
        model = models.ActionsLogEntry
        fields = (
            "id",
            "username",
            "when",
            "what",
        )
