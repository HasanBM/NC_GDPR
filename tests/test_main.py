import json
import pytest
import boto3
from moto import mock_s3
from src.utils import process_gdpr_obfuscation

@pytest.fixture
def mock_s3_bucket():
    """Create a mocked S3 bucket using Moto."""
    with mock_s3():
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name)
        yield s3_client, bucket_name

@pytest.fixture
def mock_event():
    return {
        "file_to_obfuscate": "s3://test-bucket/test.csv",
        "pii_fields": ["name", "email_address"]
    }

@pytest.fixture
def sample_csv():
    return "student_id,name,email_address\n1234,John Smith,john.smith@email.com\n5678,Jane Doe,jane.doe@email.com"

@mock_s3
def test_process_gdpr_obfuscation(mock_s3_bucket, mock_event, sample_csv):
    """Test the end-to-end GDPR obfuscation process."""
    s3_client, bucket_name = mock_s3_bucket
    file_key = "test.csv"
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=sample_csv)

    result = process_gdpr_obfuscation(mock_event)
    assert result["status"] == "Success"
    assert "obfuscated" in result["obfuscated_file"]

@mock_s3
def test_main_execution(capsys, mock_s3_bucket, mock_event, sample_csv):
    """Test main function execution and output correctness."""
    s3_client, bucket_name = mock_s3_bucket
    file_key = "test.csv"
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=sample_csv)

    process_gdpr_obfuscation(mock_event)
    captured = capsys.readouterr()
    output = json.loads(captured.out.strip())

    assert output["status"] == "Success"
    assert "obfuscated" in output["obfuscated_file"]
