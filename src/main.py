import json
from utils import process_gdpr_obfuscation

def main():
    """ Main function to execute GDPR obfuscation process. """
    event = {
        "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
        "pii_fields": ["name", "email_address"]
    }
    
    result = process_gdpr_obfuscation(event)
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
