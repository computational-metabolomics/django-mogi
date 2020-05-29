from rest_framework import serializers
from mogi.models.models_galaxy import IncomingGalaxyData


class IncomingGalaxyDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IncomingGalaxyData
        fields = ('__all__')