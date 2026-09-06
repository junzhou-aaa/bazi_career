import uuid
import json
from datetime import datetime, timedelta
import click
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from bazi_career.db import get_db_connection
from bazi_career.adapters.llm.factory import get_llm_provider
from bazi_career.domain.astrology.pillars import calculate_chart, Sex
from bazi_career.domain.astrology.calendar import calculate_true_solar_time
from bazi_career.domain.astrology.models import Chart

class VerificationQuestion(BaseModel):
    year: int = Field(description="The year the event might have happened")
    question_text: str = Field(description="The text of the question (must be in English)")
    options: Dict[str, str] = Field(description="Multiple choice options A, B, C, D (must be in English)")

class QuestionList(BaseModel):
    questions: List[VerificationQuestion]

class RecalibrationResult(BaseModel):
    reasoning: str = Field(description="Step-by-step reasoning in English to determine the favorable elements and verify the birth time.")
    favorable_elements: List[str] = Field(description="List of favorable elements (e.g., 'Wood', 'Fire', 'Earth', 'Metal', 'Water'). MUST be in English.")
    persona_notes: str = Field(description="Behavioral and astrological observations. MUST be written entirely in English.")
    suggested_time_shift_minutes: int = Field(description="Suggested shift in minutes. 0 if correct.")
    posterior_confidence: float = Field(description="Confidence score between 0.0 and 1.0.")

def get_chart_and_profile(profile_id: str):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM birth_profiles WHERE profile_id = ?", (profile_id,)).fetchone()
        
    if not row:
        raise ValueError(f"No birth profile found for profile ID {profile_id}")
        
    # calculate chart
    dt_str = row['birth_date']
    if row['birth_time']:
        dt_str += f" {row['birth_time']}"
    else:
        dt_str += " 00:00"
        
    local_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    tz_name = row['timezone'] or "Asia/Shanghai"
    tst = calculate_true_solar_time(local_dt, row['longitude'], tz_name)
    is_southern = (row['latitude'] < 0)
    sex_enum = Sex.MALE if row['sex'] == 'male' else Sex.FEMALE
    
    bazi_chart = calculate_chart(
        profile_id=profile_id,
        dt_true_solar=tst,
        sex=sex_enum,
        is_southern=is_southern,
        known_time=bool(row['birth_time'])
    )
    return dict(row), bazi_chart

def run_recalibration_workflow(profile_id: str):
    click.echo(f"Starting recalibration for profile: {profile_id}")
    
    # 1. Load data
    profile_data, bazi_chart = get_chart_and_profile(profile_id)
    llm = get_llm_provider()
    
    # 2. Pass 1: Question Generation
    click.echo("Analyzing chart for turbulent years...")
    chart_json = bazi_chart.model_dump_json()
    
    system_prompt_1 = (
        "You are an expert BaZi (Four Pillars of Destiny) astrologer. "
        "You MUST output all text, questions, and options in English. "
        "Your task is to review a BaZi chart and identify 3 turbulent or significant astrological years "
        "in the past decade (e.g., clashes, combinations, or major transitions). "
        "For each year, generate a multiple-choice question to verify actual life events to help calibrate the chart's exact birth time and favorable elements."
    )
    
    user_prompt_1 = f"Here is the BaZi chart data:\n{chart_json}\n\nPlease generate 3 multiple-choice questions."
    
    questions_resp = llm.generate_structured(
        system_prompt=system_prompt_1,
        user_prompt=user_prompt_1,
        response_model=QuestionList
    )
    
    # 3. Interactive CLI Loop
    answers = []
    for i, q in enumerate(questions_resp.questions):
        click.echo(f"\nQuestion {i+1} (Year: {q.year}):")
        click.echo(q.question_text)
        
        unique_choices = []
        for k, v in q.options.items():
            click.echo(f"{k}) {v}")
            unique_choices.append(k.upper())
        
        ans = click.prompt("Your answer", type=click.Choice(unique_choices, case_sensitive=False))
        ans_upper = ans.upper()
        
        answers.append({
            "year": q.year,
            "question": q.question_text,
            "options": q.options,
            "user_answer": ans_upper,
            "user_answer_text": q.options.get(ans_upper, q.options.get(ans_upper.lower(), ""))
        })
        
    # 4. Pass 2: Analysis & Database Update
    click.echo("\nAnalyzing your answers to calibrate the chart...")
    
    system_prompt_2 = (
        "You are an expert BaZi astrologer. You will be provided with a BaZi chart and the user's answers to verification questions. "
        "Your task is to determine the user's favorable elements (yong shen), generate behavioral/astrological persona notes, "
        "and suggest if the birth time needs to be shifted (in minutes, use 0 if correct, or a positive/negative integer). "
        "Also provide a posterior confidence score between 0.0 and 1.0. "
        "CRITICAL INSTRUCTION: You MUST provide your step-by-step reasoning. "
        "CRITICAL INSTRUCTION: All output fields (including reasoning, favorable_elements, and persona_notes) MUST be written entirely in English. Do NOT output any Chinese characters."
    )
    
    answers_json = json.dumps(answers, indent=2)
    user_prompt_2 = f"BaZi Chart:\n{chart_json}\n\nUser Answers:\n{answers_json}\n\nPlease provide your recalibration results."
    
    recalibration_resp = llm.generate_structured(
        system_prompt=system_prompt_2,
        user_prompt=user_prompt_2,
        response_model=RecalibrationResult
    )
    
    # 5. Database Update
    record_id = f"cal_{uuid.uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO calibration_records 
            (id, profile_id, notes, posterior_confidence, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            record_id, 
            profile_id, 
            recalibration_resp.persona_notes, 
            recalibration_resp.posterior_confidence, 
            now
        ))
        conn.commit()
        
    click.echo("\n--- Recalibration Results ---")
    click.echo(f"Favorable Elements: {', '.join(recalibration_resp.favorable_elements)}")
    click.echo(f"Persona Notes: {recalibration_resp.persona_notes}")
    click.echo(f"Confidence: {recalibration_resp.posterior_confidence:.2f}")
    
    shift_mins = recalibration_resp.suggested_time_shift_minutes
    if shift_mins != 0:
        click.echo(f"\n⚠️ The AI suggests your birth time might be slightly off by {shift_mins} minutes.")
        if click.confirm(f"Would you like to shift your birth time by {shift_mins} minutes?"):
            if profile_data['birth_time']:
                dt_str = f"{profile_data['birth_date']} {profile_data['birth_time']}"
                current_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                new_dt = current_dt + timedelta(minutes=shift_mins)
                
                new_date_str = new_dt.strftime("%Y-%m-%d")
                new_time_str = new_dt.strftime("%H:%M")
                
                with get_db_connection() as conn:
                    conn.execute("""
                        UPDATE birth_profiles 
                        SET birth_date = ?, birth_time = ?, updated_at = ?
                        WHERE profile_id = ?
                    """, (new_date_str, new_time_str, now, profile_id))
                    conn.commit()
                click.echo(f"Birth time updated to {new_date_str} {new_time_str}.")
            else:
                click.echo("Cannot shift time because original birth time is unknown.")
    else:
        click.echo("\nThe AI confirms your birth time appears to be accurate based on your life events.")
        
    click.echo("\n--- Next Steps ---")
    if recalibration_resp.posterior_confidence >= 0.70:
        click.echo(f"✅ Your chart confidence is {recalibration_resp.posterior_confidence:.2f} (>= 0.70). It's recommended to proceed with `bazi-career career-analyze`.")
    else:
        click.echo(f"⚠️ Your chart confidence is {recalibration_resp.posterior_confidence:.2f} (< 0.70). You may want to run `bazi-career recalibrate` again for better accuracy before proceeding to `bazi-career career-analyze`.")
        
    click.echo("\nRecalibration complete!")
