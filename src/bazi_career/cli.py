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

@cli.command(name="profile-create")
def profile_create():
    "Create a new birth profile."
    click.echo("Creating profile...")

@cli.command(name="chart")
def chart():
    "Generate Four Pillars chart."
    click.echo("Generating chart...")

@cli.command(name="validate")
def validate_cmd():
    "Run historical validation workflow."
    click.echo("Validating historical events...")

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

@cli.command(name="plan-generate")
def plan_generate():
    "Generate career plan."
    click.echo("Generating plan...")

@cli.command(name="doctor")
def doctor():
    "Check system configuration and capabilities."
    click.echo("Running doctor checks...")
