from rest_framework import serializers
from .models import Consignment, Stages, Tracker


class ConsignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consignment
        fields = "__all__"


class TrackerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tracker
        fields = ("user_id",)


class GetTeaserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Consignment
        fields = ("bill_of_ladding",)


# stage serializer
class StageSerializer(serializers.ModelSerializer):
    tracker = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Stages
        fields = (
            "tracker",
            "shipping_status",
            "created_at",
            "updated",
        )
        read_only_fields = ("shipping_status", "created_at", "updated")

    def get_tracker(self, obj):
        return {
            "tracking_id": obj.tracker.tracking_id,
            "bill_of_ladding": obj.tracker.consignment.bill_of_ladding,
        }
