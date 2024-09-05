import logging

from django.apps import apps
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector
from model_utils.models import StatusModel
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from govapp.apps.accounts.serializers import UserKeyValueListSerializer
from govapp.apps.main.mixins import KeyValueListMixin

from .models import (
    AssignableModel,
    District,
    EndorsableModel,
    ReferenceableModel,
    Region,
)
from .serializers import (
    AssignedItemSerializer,
    DistrictSerializer,
    RegionSerializer,
    SearchSerializer,
)

logger = logging.getLogger(__name__)


User = auth.get_user_model()


class RegionViewSet(KeyValueListMixin, viewsets.ReadOnlyModelViewSet):
    """Region viewset"""

    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class DistrictViewSet(KeyValueListMixin, viewsets.ReadOnlyModelViewSet):
    """District viewset"""

    queryset = District.objects.all()
    serializer_class = DistrictSerializer


class AssignToMeAPIView(APIView):
    """An api end point that allows the request user to assign an object to themselves
    so long as the model the object is based on extends from AssignableModel

    Request type must be POST with parameters: content_type and object_id
    """

    def post(self, request, format=None):
        content_type = request.data.get("content_type", None)
        if not content_type:
            raise ValidationError("AssignToMeAPIView requires a content type")

        try:
            ContentType.objects.get(id=content_type)
        except ContentType.DoesNotExist:
            raise ValidationError(f"No content type found with id: {content_type}")

        object_id = request.data.get("object_id", None)
        if not object_id:
            raise ValidationError("AssignToMeAPIView requires an object id")

        model_class = ContentType.objects.get(id=content_type).model_class()

        try:
            instance = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            raise ValidationError(
                "No object found with content_type: {} and object_id: {}".format(
                    content_type, object_id
                )
            )

        if not isinstance(instance, AssignableModel):
            raise ValidationError(
                "The model the object is based on must extend from AssignableModel"
            )

        if not instance.user_is_assignable(request.user):
            raise ValidationError(
                "You are not in the list of assignable users for this object"
            )

        logger.info(
            f"Assigning: {instance._meta.object_name} {instance} to {request.user} (request user)"
        )

        instance.assign(request.user)

        logger.info(
            f"Assigned: {instance._meta.object_name} {instance} to {request.user} (request user)"
        )

        return Response({"user_id": request.user.id}, status=status.HTTP_200_OK)


class AssignableUsersAPIView(APIView):
    """An api end point that returns a list of users that can be assign to a model instance
      as the model the object is based on extends from AssignableModel

    Request type must be GET with parameters: content_type and object_id
    """

    def get(self, request, format=None):
        content_type = request.query_params.get("content_type", None)
        if not content_type:
            raise ValidationError("AssignableUsers requires a content type")

        try:
            ContentType.objects.get(id=content_type)
        except ContentType.DoesNotExist:
            raise ValidationError(f"No content type found with id: {content_type}")

        object_id = request.query_params.get("object_id", None)
        if not object_id:
            raise ValidationError("AssignableUsers requires an object id")

        model_class = ContentType.objects.get(id=content_type).model_class()

        try:
            instance = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            raise ValidationError(
                "No object found with content_type: {} and object_id: {}".format(
                    content_type, object_id
                )
            )

        if not isinstance(instance, AssignableModel):
            raise ValidationError(
                "The model the object is based on must extend from AssignableModel"
            )

        assignable_users = instance.assignable_users()

        serializer = UserKeyValueListSerializer(assignable_users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignToAPIView(APIView):
    """An api end point that allows the request user to assign an object to themselves
    so long as the model the object is based on extends from AssignableModel

    Request type must be POST with parameters: content_type, object_id and user_id
    """

    def post(self, request, format=None):
        content_type = request.data.get("content_type", None)
        if not content_type:
            raise ValidationError("AssignToMeAPIView requires a content type")

        try:
            ContentType.objects.get(id=content_type)
        except ContentType.DoesNotExist:
            raise ValidationError(f"No content type found with id: {content_type}")

        object_id = request.data.get("object_id", None)
        if not object_id:
            raise ValidationError("AssignToMeAPIView requires an object id")

        model_class = ContentType.objects.get(id=content_type).model_class()

        try:
            instance = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            raise ValidationError(
                "No object found with content_type: {} and object_id: {}".format(
                    content_type, object_id
                )
            )

        if not isinstance(instance, AssignableModel):
            raise ValidationError(
                "The model the object is based on must extend from AssignableModel"
            )

        user_id = request.data.get("user_id", None)
        if not user_id:
            instance.assign(None)
            return Response(status=status.HTTP_200_OK)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError(f"No user found with id: {user_id}")

        if not instance.user_is_assignable(user):
            raise ValidationError(
                f"{user} is not in the list of assignable users for this object"
            )

        logger.info(f"Assigning: {instance._meta.object_name} {instance} to {user}")

        instance.assign(user)

        logger.info(f"Assigned: {instance._meta.object_name} {instance} to {user}")

        return Response(status=status.HTTP_200_OK)


class SearchViewSet(viewsets.ViewSet):
    """Search viewset"""

    def list(self, request):
        """List of search results"""
        query = request.query_params.get("q", None)
        if not query:
            return Response([], status=status.HTTP_200_OK)

        search_vector = SearchVector("reference_number", "name")

        models_to_search = []
        for model in apps.get_models():
            if (
                issubclass(model, ReferenceableModel)
                and issubclass(model, StatusModel)
                and hasattr(model, "name")
            ):
                models_to_search.append(model)

        queryset = (
            models_to_search[0]
            .objects.annotate(search=search_vector)
            .filter(search=query)
            .only("id", "reference_number", "name", "status")
        )
        for model in models_to_search[1:]:
            union_queryset = queryset.union(
                model.objects.annotate(search=search_vector)
                .filter(search=query)
                .only("id", "reference_number", "name", "status")
            )
            queryset = queryset.union(union_queryset)

        results = SearchSerializer(
            queryset,
            context={"request": request},
            many=True,
        ).data

        return Response(results, status=status.HTTP_200_OK)


class AssignedItemsViewSet(viewsets.ViewSet):
    """ViewSet that returns a list of items that are assigned to the requeust user"""

    def list(self, request):
        """List of items the request user is assigned to"""
        models_to_search = []
        for model in apps.get_models():
            if (
                issubclass(model, AssignableModel)
                and hasattr(model, "status")
                and hasattr(model, "name")
                and hasattr(model, "created")
            ):
                models_to_search.append(model)

        queryset = (
            models_to_search[0]
            .objects.filter(assigned_to=request.user)
            .only("id", "reference_number", "name", "status", "created")
        )
        for model in models_to_search[1:]:
            union_queryset = queryset.union(
                model.objects.filter(assigned_to=request.user).only(
                    "id", "reference_number", "name", "status", "created"
                )
            )
            queryset = queryset.union(union_queryset)

        queryset = queryset.order_by("-created")

        serializer = AssignedItemSerializer(
            queryset,
            context={"request": request},
            many=True,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class EndorsingItemsViewSet(viewsets.ViewSet):
    """ViewSet that returns a list of items that are requiring endorsment from the requeust user"""

    def list(self, request):
        """List of items that are requiring endorsment from the request user"""
        models_to_search = []
        for model in apps.get_models():
            if (
                issubclass(model, EndorsableModel)
                and hasattr(model, "status")
                and hasattr(model, "name")
                and hasattr(model, "created")
            ):
                models_to_search.append(model)

        queryset = (
            models_to_search[0]
            .objects.filter(seeking_endorsement_from=request.user)
            .only("id", "reference_number", "name", "status", "created")
        )
        for model in models_to_search[1:]:
            union_queryset = queryset.union(
                model.objects.filter(seeking_endorsement_from=request.user).only(
                    "id", "reference_number", "name", "status", "created"
                )
            )
            queryset = queryset.union(union_queryset)

        queryset = queryset.order_by("-created")

        serializer = AssignedItemSerializer(
            queryset,
            context={"request": request},
            many=True,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
