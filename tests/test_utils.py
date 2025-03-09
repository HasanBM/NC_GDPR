import pytest
import boto3
import pandas as pd
import io
from moto import mock_s3
from src.utils import extract_from_s3, obfuscate_pii, load_to_s3, process_gdpr_obfuscation

@pytest.fixture
def mock_s3_bucket():
    with mock_s3():
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name)
        yield s3_client, bucket_name

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "student_id": [1234, 5678],
        "name": ["John Smith", "Jane Doe"],
        "email_address": ["john.smith@email.com", "jane.doe@email.com"]
    })

@pytest.fixture
def sample_csv():
    return "student_id,name,email_address\n1234,John Smith,john.smith@email.com\n5678,Jane Doe,jane.doe@email.com"

def test_extract_from_s3(mock_s3_bucket, sample_csv):
    s3_client, bucket_name = mock_s3_bucket
    file_key = "test.csv"
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=sample_csv)
    df = extract_from_s3(bucket_name, file_key)
    assert df.shape == (2, 3)
    assert "name" in df.columns

def test_obfuscate_pii(sample_dataframe):
    pii_fields = ["name", "email_address"]
    obfuscated_df = obfuscate_pii(sample_dataframe, pii_fields)
    assert all(obfuscated_df["name"] == "***")
    assert all(obfuscated_df["email_address"] == "***")

def test_load_to_s3(mock_s3_bucket, sample_dataframe):
    s3_client, bucket_name = mock_s3_bucket
    file_key = "obfuscated.csv"
    load_to_s3(sample_dataframe, bucket_name, file_key)
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    assert response["Body"].read().decode("utf-8").startswith("student_id,name,email_address")

def test_process_gdpr_obfuscation(mock_s3_bucket, sample_csv):
    s3_client, bucket_name = mock_s3_bucket
    file_key = "new_data/test.csv"
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=sample_csv)
    event = {"file_to_obfuscate": f"s3://{bucket_name}/{file_key}", "pii_fields": ["name", "email_address"]}
    result = process_gdpr_obfuscation(event)
    assert result["status"] == "Success"
    assert "obfuscated" in result["obfuscated_file"]
