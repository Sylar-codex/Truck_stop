from rest_framework import serializers
from .utils import TruckStops, get_total_amount


class DestinationSerializer(serializers.Serializer) :
    start = serializers.CharField()
    finish = serializers.CharField()

    def save(self) :
        start = self.validated_data['start']
        finish = self.validated_data['finish']       

        # function to get routes
        stops = TruckStops().get_routes(start,finish)
        
        total_amount = get_total_amount(stops['city_routes'])
            
        return {"stop_routes":stops,"total_amount":total_amount}
    



# test_ad_1 = "1234 Elm Street, Apt 56B, Springfield, IL 62704, USA"
# test_ad_2 = "789 Oak Avenue, Suite 201, Dallas, TX 75201, USA"
