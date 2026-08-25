from click.testing import CliRunner
from bazi_career.cli import cli
from bazi_career.db import get_config, init_db

def test_configure_command(monkeypatch, tmp_path):
    # Use a temporary database file in the sandbox
    test_db = tmp_path / "test.db"
    monkeypatch.setattr("bazi_career.db.DB_PATH", test_db)
    monkeypatch.setattr("bazi_career.db.DATA_DIR", tmp_path)
    
    init_db(test_db) # ensure db exists
    runner = CliRunner()
    result = runner.invoke(cli, ['configure'], input='openai\nfake_api_key\n')
    
    assert result.exit_code == 0
    assert "Configuration saved securely" in result.output
    
    # verify db
    assert get_config("llm_provider") == "openai"
    assert get_config("openai_api_key") == "fake_api_key"

def test_configure_deepseek(monkeypatch, tmp_path):
    test_db = tmp_path / "test2.db"
    monkeypatch.setattr("bazi_career.db.DB_PATH", test_db)
    monkeypatch.setattr("bazi_career.db.DATA_DIR", tmp_path)
    
    init_db(test_db)
    runner = CliRunner()
    result = runner.invoke(cli, ['configure'], input='deepseek\ndeepseek_api_key\n')
    
    assert result.exit_code == 0
    assert get_config("llm_provider") == "deepseek"
    assert get_config("deepseek_api_key") == "deepseek_api_key"
