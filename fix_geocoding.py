import re

with open("src/bazi_career/cli.py", "r") as f:
    content = f.read()

profile_create_code = """
import uuid
from datetime import datetime
from bazi_career.db import get_db_connection

@cli.command(name="profile-create")
def profile_create():
    "Create a new birth profile interactively."
    click.echo("🔮 Let's set up your Bazi Profile!")
    
    # 1. Collect Details
    sex_input = click.prompt("Sex (M/F)", type=click.Choice(['M', 'F', 'm', 'f']))
    sex = "male" if sex_input.upper() == 'M' else "female"
    
    birth_date = click.prompt("Birth Date (YYYY-MM-DD)")
    birth_time = click.prompt("Birth Time (HH:MM, or press Enter if unknown)", default="", show_default=False)
    
    birth_place = click.prompt("Birth Place (e.g., Beijing, China)")
    
    # Use real geocoding
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    
    click.echo(f"🌍 Resolving coordinates for '{birth_place}'...")
    try:
        geolocator = Nominatim(user_agent="bazi_career_cli")
        location = geolocator.geocode(birth_place)
        
        if not location:
            click.echo(f"⚠️ Could not find '{birth_place}'. Defaulting to Beijing.", err=True)
            longitude = 116.4
            latitude = 39.9
            tz_str = "Asia/Shanghai"
        else:
            longitude = location.longitude
            latitude = location.latitude
            click.echo(f"   -> Found: {location.address} (Lat: {latitude:.2f}, Lon: {longitude:.2f})")
            
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lng=longitude, lat=latitude)
            if not tz_str:
                click.echo(f"⚠️ Could not find timezone. Defaulting to UTC.", err=True)
                tz_str = "UTC"
            click.echo(f"   -> Timezone: {tz_str}")
    except Exception as e:
        click.echo(f"⚠️ Geocoding failed: {str(e)}. Defaulting to Beijing.", err=True)
        longitude = 116.4
        latitude = 39.9
        tz_str = "Asia/Shanghai"
    
    # 2. Process Data
    profile_id = f"usr_{uuid.uuid4().hex[:8]}"
    birth_profile_id = f"bp_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    # 3. Save to DB
    try:
        with get_db_connection() as conn:
            conn.execute("INSERT INTO profiles (id, created_at, updated_at) VALUES (?, ?, ?)", 
                         (profile_id, now, now))
            
            conn.execute(\"\"\"
                INSERT INTO birth_profiles 
                (id, profile_id, birth_date, birth_time, birth_time_precision, birth_place_text, timezone, longitude, latitude, sex, calendar, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (
                birth_profile_id, profile_id, birth_date, birth_time if birth_time else None,
                "minute" if birth_time else "day", birth_place, tz_str, longitude, latitude, sex, "solar", now, now
            ))
            conn.commit()
            
        click.echo("-" * 30)
        click.echo(f"✅ Profile created successfully!")
        click.echo(f"👤 Profile ID: {profile_id} (Keep this ID to generate your plan!)")
        click.echo("-" * 30)
        click.echo(f"Next step: Run `bazi-career chart --profile-id {profile_id}` to calculate your Bazi.")
    except Exception as e:
        click.echo(f"Error saving profile: {str(e)}", err=True)
"""

chart_code = """
from bazi_career.domain.astrology.calendar import calculate_true_solar_time
from bazi_career.domain.astrology.pillars import calculate_chart, Sex
import json
from datetime import datetime

@cli.command(name="chart")
@click.option('--profile-id', required=True, help="User profile ID.")
def chart(profile_id):
    "Generate Four Pillars chart from the database."
    from bazi_career.db import get_db_connection
    
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM birth_profiles WHERE profile_id = ?", (profile_id,)).fetchone()
        
    if not row:
        click.echo(f"Error: No birth profile found for ID {profile_id}", err=True)
        return
        
    click.echo(f"Calculating astrological chart for {profile_id}...")
    
    dt_str = row['birth_date']
    if row['birth_time']:
        dt_str += f" {row['birth_time']}"
    else:
        dt_str += " 00:00"
        
    local_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    tz_name = row['timezone'] or "Asia/Shanghai"
    
    tst = calculate_true_solar_time(local_dt, row['longitude'], tz_name)
    
    click.echo(f"  - Local Time: {local_dt} ({tz_name})")
    click.echo(f"  - True Solar Time: {tst} (Adjusted for longitude & equation of time)")
    
    is_southern = (row['latitude'] < 0)
    if is_southern:
        click.echo(f"  - Southern Hemisphere detected (Lat: {row['latitude']:.2f}). Applying seasonal adjustment.")
        
    sex_enum = Sex.MALE if row['sex'] == 'male' else Sex.FEMALE
    
    # Calculate Pillars
    try:
        bazi_chart = calculate_chart(
            profile_id=profile_id,
            dt_true_solar=tst,
            sex=sex_enum,
            is_southern=is_southern,
            known_time=bool(row['birth_time'])
        )
        
        click.echo("-" * 30)
        click.echo(f"Year Pillar:  {bazi_chart.year_pillar.stem}{bazi_chart.year_pillar.branch}")
        click.echo(f"Month Pillar: {bazi_chart.month_pillar.stem}{bazi_chart.month_pillar.branch}")
        click.echo(f"Day Pillar:   {bazi_chart.day_pillar.stem}{bazi_chart.day_pillar.branch}")
        if bazi_chart.hour_pillar:
            click.echo(f"Hour Pillar:  {bazi_chart.hour_pillar.stem}{bazi_chart.hour_pillar.branch}")
        else:
            click.echo(f"Hour Pillar:  [Unknown Time]")
            
        click.echo(f"Day Master:   {bazi_chart.day_master}")
        click.echo(f"Luck Direction: {bazi_chart.luck_direction} (Starts at {bazi_chart.start_of_luck} year)")
        
        click.echo("-" * 30)
        click.echo("✅ Chart successfully calculated! You can now run `bazi-career validate` or `plan-generate`.")
        
    except Exception as e:
        click.echo(f"Error calculating chart: {str(e)}", err=True)
"""

content = re.sub(
    r'@cli\.command\(name="profile-create"\).*?except Exception as e:\n\s+click\.echo\(f"Error saving profile: \{str\(e\)\}", err=True\)',
    profile_create_code.strip(),
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'from bazi_career\.domain\.astrology\.calendar import calculate_true_solar_time.*?except Exception as e:\n\s+click\.echo\(f"Error calculating chart: \{str\(e\)\}", err=True\)',
    chart_code.strip(),
    content,
    flags=re.DOTALL
)

with open("src/bazi_career/cli.py", "w") as f:
    f.write(content)
