from rest_framework import serializers
from mogi.models import IncomingGalaxyData


class IncomingGalaxyDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncomingGalaxyData
        fields = ('__all__')