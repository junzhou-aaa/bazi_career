import click

@click.group()
@click.version_option()
def cli():
    "Bazi Career Planning CLI"
    pass

from bazi_career.db import init_db

@cli.command(name="init")
def init():
    "Initialize local data and LLM configuration."
    click.echo("Initializing Bazi Career...")
    init_db()
    click.echo("Database initialized.")

from bazi_career.db import set_config, get_config

@cli.command(name="configure")
def configure():
    "Configure API keys and providers (BYOK)."
    click.echo("We will ask for your API key and all data is saved in your local database.")
    provider = click.prompt(
        "Pls first choose the LLM provider",
        type=click.Choice(["openai", "anthropic", "deepseek"]),
        show_default=False
    )
    set_config("llm_provider", provider)
    
    if provider == "openai":
        api_key = click.prompt("Enter OpenAI API Key", hide_input=True)
        set_config("openai_api_key", api_key)
    elif provider == "anthropic":
        api_key = click.prompt("Enter Anthropic API Key", hide_input=True)
        set_config("anthropic_api_key", api_key)
    elif provider == "deepseek":
        api_key = click.prompt("Enter DeepSeek API Key", hide_input=True)
        set_config("deepseek_api_key", api_key)
        
    click.echo("Configuration saved securely to local database.")

import uuid
from datetime import datetime
from bazi_career.db import get_db_connection

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
            
            conn.execute("""
                INSERT INTO birth_profiles 
                (id, profile_id, birth_date, birth_time, birth_time_precision, birth_place_text, timezone, longitude, latitude, sex, calendar, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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

from bazi_career.domain.astrology.calendar import calculate_true_solar_time
from bazi_career.domain.astrology.pillars import calculate_chart, Sex
import json
from datetime import datetime

def get_or_select_profile_id(provided_id: str | None) -> str:
    from bazi_career.db import get_db_connection
    with get_db_connection() as conn:
        if provided_id:
            row = conn.execute("SELECT id FROM profiles WHERE id = ?", (provided_id,)).fetchone()
            if not row:
                click.echo(f"Error: Profile '{provided_id}' not found.", err=True)
                raise click.Abort()
            return provided_id
            
        rows = conn.execute("""
            SELECT p.id, bp.birth_date, bp.birth_place_text 
            FROM profiles p 
            LEFT JOIN birth_profiles bp ON p.id = bp.profile_id
            ORDER BY p.created_at DESC
        """).fetchall()
        
        if not rows:
            click.echo("No profiles found. Please run `bazi-career profile-create` first.", err=True)
            raise click.Abort()
            
        if len(rows) == 1:
            click.echo(f"Auto-selected profile: {rows[0]['id']} (Born: {rows[0]['birth_date']})")
            return rows[0]['id']
            
        click.echo("Multiple profiles found. Please select one:")
        choices = []
        for i, row in enumerate(rows, 1):
            desc = f"{row['id']} (Born: {row['birth_date'] or 'Unknown'} at {row['birth_place_text'] or 'Unknown'})"
            click.echo(f"{i}. {desc}")
            choices.append(str(i))
            
        choice = click.prompt("Enter the number of the profile", type=click.Choice(choices))
        return rows[int(choice) - 1]['id']


@cli.command(name="chart")
@click.option('--profile-id', required=False, help="User profile ID. Auto-detected if not provided.")
def chart(profile_id):
    "Generate Four Pillars chart from the database."
    profile_id = get_or_select_profile_id(profile_id)
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

from bazi_career.application.validation_workflow import run_validation_workflow

@cli.command(name="validate")
@click.option('--profile-id', required=False, help="User profile ID to validate. Auto-detected if not provided.")
def validate_cmd(profile_id):
    "Run historical validation workflow."
    profile_id = get_or_select_profile_id(profile_id)
    click.echo(f"Validating historical events for {profile_id}...")
    
    # Mock data for demonstration
    mock_chart = {"day_master": "甲", "five_elements": {"甲": "木", "子": "水"}}
    mock_career = {"experience": [{"company": "Tech Corp", "role": "Engineer", "year": "2020"}]}
    
    try:
        response = run_validation_workflow(profile_id, mock_chart, mock_career)
        click.echo(f"Validation complete. Confidence Score: {response.confidence_score}")
        click.echo(f"Summary: {response.summary}")
    except Exception as e:
        click.echo(f"Error during validation: {str(e)}", err=True)

from bazi_career.application.recalibration_workflow import run_recalibration_workflow

@cli.command(name="recalibrate")
@click.option('--profile-id', required=False, help="User profile ID. Auto-detected if not provided.")
def recalibrate(profile_id):
    "Recalibrate the model."
    profile_id = get_or_select_profile_id(profile_id)
    try:
        run_recalibration_workflow(profile_id)
    except Exception as e:
        click.echo(f"Error during recalibration: {str(e)}", err=True)

@cli.command(name="career-analyze")
def career_analyze():
    "Analyze career profile."
    click.echo("Analyzing career profile...")

@cli.command(name="jobs-discover")
def jobs_discover():
    "Discover job opportunities."
    click.echo("Discovering jobs...")

@cli.command(name="jobs-rank")
def jobs_rank():
    "Rank discovered jobs."
    click.echo("Ranking jobs...")

from bazi_career.application.planning_workflow import run_planning_workflow

@cli.command(name="plan-generate")
@click.option('--profile-id', required=False, help="User profile ID to generate plan for. Auto-detected if not provided.")
def plan_generate(profile_id):
    "Generate career plan."
    profile_id = get_or_select_profile_id(profile_id)
    click.echo(f"Generating plan for {profile_id}...")
    
    # Mock data for demonstration
    mock_chart = {"day_master": "甲", "five_elements": {"甲": "木", "子": "水"}}
    mock_career = {"experience": [{"company": "Tech Corp", "role": "Engineer", "year": "2020"}], "skills": ["Python"]}
    
    try:
        plan = run_planning_workflow(profile_id, mock_chart, mock_career, validation_confidence=0.85)
        click.echo("Plan generated successfully!")
        click.echo("-" * 40)
        click.echo(plan.content_md)
        click.echo("-" * 40)
    except Exception as e:
        click.echo(f"Error during planning: {str(e)}", err=True)

@cli.command(name="doctor")
def doctor():
    "Check system configuration and capabilities."
    click.echo("Running doctor checks...")
