import pytest
import boto3
import pandas as pd
import io
from moto import mock_s3


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


