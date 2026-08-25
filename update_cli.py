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
    name = click.prompt("Name/Alias")
    sex_input = click.prompt("Sex (M/F)", type=click.Choice(['M', 'F', 'm', 'f']))
    sex = "male" if sex_input.upper() == 'M' else "female"
    
    birth_date = click.prompt("Birth Date (YYYY-MM-DD)")
    birth_time = click.prompt("Birth Time (HH:MM, or press Enter if unknown)", default="", show_default=False)
    
    birth_place = click.prompt("Birth Place (e.g., Beijing, China)")
    longitude = click.prompt("Longitude (e.g., 116.4 for Beijing, -74.0 for NY)", type=float)
    latitude = click.prompt("Latitude (e.g., 39.9 for Beijing, -33.8 for Sydney)", type=float)
    
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
                (id, profile_id, birth_date, birth_time, birth_time_precision, birth_place_text, longitude, latitude, sex, calendar, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (
                birth_profile_id, profile_id, birth_date, birth_time if birth_time else None,
                "minute" if birth_time else "day", birth_place, longitude, latitude, sex, "solar", now, now
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

# Replace old profile_create
content = re.sub(
    r'@cli\.command\(name="profile-create"\)\ndef profile_create\(\):\n\s+"Create a new birth profile\."\n\s+click\.echo\("Creating profile\.\.\."\)',
    profile_create_code.strip(),
    content
)

with open("src/bazi_career/cli.py", "w") as f:
    f.write(content)
