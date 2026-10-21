"""Geospatial helpers used by the emergency source-matching engine."""
from math import asin, cos, radians, sin, sqrt


EARTH_RADIUS_KM = 6371.0088


def haversine_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Return great-circle distance between two WGS84 coordinate pairs in km.

    This estimates geographic distance, not road travel distance or ETA.
    Inputs are range-checked so missing/invalid coordinates cannot quietly
    become a plausible-looking distance.
    """
    coordinates = (latitude_a, longitude_a, latitude_b, longitude_b)
    if any(value is None for value in coordinates):
        raise ValueError("All latitude and longitude values are required.")

    lat_a, lon_a, lat_b, lon_b = (float(value) for value in coordinates)
    if not (-90 <= lat_a <= 90 and -90 <= lat_b <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not (-180 <= lon_a <= 180 and -180 <= lon_b <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    phi_a, phi_b = radians(lat_a), radians(lat_b)
    delta_phi = radians(lat_b - lat_a)
    delta_lambda = radians(lon_b - lon_a)

    haversine = (
        sin(delta_phi / 2) ** 2
        + cos(phi_a) * cos(phi_b) * sin(delta_lambda / 2) ** 2
    )
    # Clamp against floating-point drift near antipodal points.
    haversine = min(1.0, max(0.0, haversine))
    return EARTH_RADIUS_KM * 2 * asin(sqrt(haversine))
