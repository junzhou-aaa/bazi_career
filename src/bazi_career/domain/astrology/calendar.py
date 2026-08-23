import math
from datetime import datetime, timedelta, time
import pytz

def get_equation_of_time(dt: datetime) -> float:
    """
    Calculate Equation of Time (均时差) in minutes for a given date.
    Uses the standard empirical formula.
    """
    day_of_year = dt.timetuple().tm_yday
    B = 2 * math.pi * (day_of_year - 81) / 365.24
    eot = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    return eot

def calculate_true_solar_time(
    dt_local: datetime,
    longitude: float,
    tz_name: str
) -> datetime:
    """
    Calculates True Solar Time (真太阳时) following strict 4 steps:
    1. Deduct DST (automatically handled by comparing tz offset to base offset).
    2. Longitude difference (1 degree = 4 minutes).
    3. Local Mean Time (平太阳时).
    4. Equation of Time (均时差).
    """
    tz = pytz.timezone(tz_name)
    # Ensure dt_local is localized
    if dt_local.tzinfo is None:
        dt_local = tz.localize(dt_local)
        
    # 1. Deduct DST to get local standard time
    # We find the standard offset for this timezone (no DST)
    # A simple way is to take the offset and subtract the DST offset (dst() method)
    dst_offset = dt_local.dst()
    if dst_offset:
        dt_standard = dt_local - dst_offset
    else:
        dt_standard = dt_local
        
    # Standard offset in hours from UTC
    base_utc_offset = dt_local.utcoffset() - dt_local.dst()
    utc_offset_seconds = base_utc_offset.total_seconds()
    center_longitude = (utc_offset_seconds / 3600) * 15.0
    
    # 2 & 3. Longitude difference and Local Mean Time (平太阳时)
    # 1 degree = 4 minutes
    longitude_diff = longitude - center_longitude
    lmt_offset_minutes = longitude_diff * 4
    
    dt_lmt = dt_standard + timedelta(minutes=lmt_offset_minutes)
    
    # 4. Equation of Time (均时差)
    eot_minutes = get_equation_of_time(dt_lmt)
    
    # True Solar Time (真太阳时)
    dt_true_solar = dt_lmt + timedelta(minutes=eot_minutes)
    
    return dt_true_solar

def is_southern_hemisphere(latitude: float) -> bool:
    """Return True if latitude is in the Southern Hemisphere."""
    return latitude < 0.0
