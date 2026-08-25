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
    provider = click.prompt("Select LLM Provider", type=click.Choice(["openai", "anthropic", "deepseek"]), default="openai")
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

@cli.command(name="profile-create")
def profile_create():
    "Create a new birth profile."
    click.echo("Creating profile...")

@cli.command(name="chart")
def chart():
    "Generate Four Pillars chart."
    click.echo("Generating chart...")

from bazi_career.application.validation_workflow import run_validation_workflow

@cli.command(name="validate")
@click.option('--profile-id', required=True, help="User profile ID to validate.")
def validate_cmd(profile_id):
    "Run historical validation workflow."
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

@cli.command(name="recalibrate")
def recalibrate():
    "Recalibrate the model."
    click.echo("Recalibrating...")

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
@click.option('--profile-id', required=True, help="User profile ID to generate plan for.")
def plan_generate(profile_id):
    "Generate career plan."
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
