import json
import pytest
from src.utils import process_gdpr_obfuscation

@pytest.fixture
def mock_event():
    return {
        "file_to_obfuscate": "s3://test-bucket/test.csv",
        "pii_fields": ["name", "email_address"]
    }

def test_process_gdpr_obfuscation(mock_event):
    result = process_gdpr_obfuscation(mock_event)
    assert result["status"] == "Success"
    assert "obfuscated" in result["obfuscated_file"]

def test_main_execution(capsys, mock_event):
    """ Test main function execution and output correctness. """
    process_gdpr_obfuscation(mock_event)  # Run the function
    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())
    assert output["status"] == "Success"
    assert "obfuscated" in output["obfuscated_file"]
