from math import radians, sin, cos, sqrt, atan2


EARTH_RADIUS_KM = 6371.0


def calculate_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """
    Calculate the great-circle distance between
    two geographic coordinates using the Haversine formula.

    Returns:
        Distance in kilometers.
    """

    lat1 = radians(float(latitude_1))
    lon1 = radians(float(longitude_1))

    lat2 = radians(float(latitude_2))
    lon2 = radians(float(longitude_2))

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return round(
        EARTH_RADIUS_KM * c,
        2
    )