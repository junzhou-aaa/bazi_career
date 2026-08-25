from click.testing import CliRunner
from bazi_career.cli import cli
from bazi_career.domain.validation.models import CalibrationRecord
from bazi_career.application.validation_workflow import ValidationResponse
from bazi_career.application.planning_workflow import CareerPlanOutput

class MockLLMProvider:
    def __init__(self, **kwargs):
        self.model = "mock-model"
        
    def generate_structured(self, system_prompt, user_prompt, response_model):
        if response_model == ValidationResponse:
            return ValidationResponse(
                calibrations=[CalibrationRecord(
                    id="rec_1", profile_id="test", hypothesis="Test",
                    evidence_ids=[], prior_confidence=0.5, posterior_confidence=0.8,
                    support=["Test Support"], counterevidence=[], created_at="2026-08-25"
                )],
                confidence_score=0.85,
                summary="Mock summary."
            )
        elif response_model == CareerPlanOutput:
            return CareerPlanOutput(
                summary="Mock summary.",
                recommended_industries=["Tech"],
                recommended_roles=["Engineer"],
                skill_gaps=["Communication"],
                timeline_1_year="Learn X",
                timeline_3_year="Do Y",
                timeline_5_year="Achieve Z",
                bazi_rationale="Because Wood is favorable."
            )

def test_validate_cmd(monkeypatch):
    monkeypatch.setattr("bazi_career.application.validation_workflow.get_llm_provider", lambda: MockLLMProvider())
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', '--profile-id', 'test1'])
    assert result.exit_code == 0
    assert "Confidence Score: 0.85" in result.output

def test_plan_generate_cmd(monkeypatch):
    monkeypatch.setattr("bazi_career.application.planning_workflow.get_llm_provider", lambda: MockLLMProvider())
    runner = CliRunner()
    result = runner.invoke(cli, ['plan-generate', '--profile-id', 'test1'])
    assert result.exit_code == 0
    assert "Bazi Career Plan" in result.output
    assert "Because Wood is favorable." in result.output
