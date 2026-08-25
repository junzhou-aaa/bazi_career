import re

with open("src/bazi_career/cli.py", "r") as f:
    content = f.read()

chart_code = """
from bazi_career.domain.astrology.calendar import calculate_true_solar_time
from bazi_career.domain.astrology.pillars import calculate_chart, Sex
import json

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
    
    # Calculate True Solar Time
    # Note: A real app would get the timezone string from DB or coordinates.
    # For MVP, we assume UTC+8 if longitude is around 120, etc., but our calculation uses base offsets.
    import pytz
    # Hardcode timezone for MVP interaction simplicity unless supplied
    tz = pytz.timezone(row['timezone'] or "Asia/Shanghai") 
    local_dt = tz.localize(local_dt)
    
    tst = calculate_true_solar_time(local_dt, row['longitude'])
    
    click.echo(f"  - Local Time: {local_dt}")
    click.echo(f"  - True Solar Time: {tst} (Adjusted for longitude & equation of time)")
    
    is_southern = (row['latitude'] < 0)
    if is_southern:
        click.echo(f"  - Southern Hemisphere detected (Lat: {row['latitude']}). Applying seasonal adjustment.")
        
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

# Replace old chart
content = re.sub(
    r'@cli\.command\(name="chart"\)\ndef chart\(\):\n\s+"Generate Four Pillars chart\."\n\s+click\.echo\("Generating chart\.\.\."\)',
    chart_code.strip(),
    content
)

with open("src/bazi_career/cli.py", "w") as f:
    f.write(content)
