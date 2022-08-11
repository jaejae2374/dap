from util.location.models import Location
from util.location.serializers import LocationSerializer

def set_location(data: dict, type: str, name: str) -> Location:
    """Set location."""
    location = data['location']
    location['type'] = type
    ls = LocationSerializer(
        data=location, 
        context={
            'images': location.get('images'),
            'name': name
        }
    )
    ls.is_valid(raise_exception=True)
    return ls.save()
