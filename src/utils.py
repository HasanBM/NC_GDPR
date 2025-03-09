import boto3
import pandas as pd
import io

def extract_from_s3(bucket_name, file_key):
    """Download file from S3 and return its content as a Pandas DataFrame."""
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def obfuscate_pii(dataframe, pii_fields):
    """Replace sensitive PII fields with obfuscated values."""
    dataframe[pii_fields] = '***'
    return dataframe

def load_to_s3(dataframe, bucket_name, file_key):
    """Upload the obfuscated DataFrame back to S3 as a CSV file."""
    s3_client = boto3.client('s3')
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=csv_buffer.getvalue())

def process_gdpr_obfuscation(event):
    """Main function to orchestrate the GDPR obfuscation process."""
    bucket_name = event["file_to_obfuscate"].split("/")[2]
    file_key = "/".join(event["file_to_obfuscate"].split("/")[3:])
    pii_fields = event["pii_fields"]
    
    df = extract_from_s3(bucket_name, file_key)
    obfuscated_df = obfuscate_pii(df, pii_fields)
    output_key = f"obfuscated/{file_key}"
    load_to_s3(obfuscated_df, bucket_name, output_key)
    
    return {"status": "Success", "obfuscated_file": f"s3://{bucket_name}/{output_key}"}
