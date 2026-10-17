import os
import urllib.parse
import awswrangler as wr
import pandas as pd

def lambda_handler(event, context):
    src_bucket = event['Records'][0]['s3']['bucket']['name']
    src_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    dest_bucket = os.environ.get('PROCESSED_BUCKET')
    
    input_uri = f"s3://{src_bucket}/{src_key}"
    df = wr.s3.read_csv(path=input_uri)
    
    # Cleaning Logic
    df['patient_name'] = df['patient_name'].astype(str).str.strip().str.title()
    df['new_id'] = pd.factorize(df['patient_name'])[0] + 1001
    df['gender'] = df['gender'].astype(str).str.strip().str.title().replace({'Male': 'M', 'Female': 'F', '0': '', '1': '', 'Nan': ''})
    df['follow_up_required'] = df['follow_up_required'].astype(str).str.strip().replace({'0': 'N', '1': 'Y', 'Yes': 'Y', 'No': 'N'})
    df['appointment_date'] = pd.to_datetime(df['appointment_date'], format='mixed', dayfirst=True)
    df['booking_date'] = pd.to_datetime(df['booking_date'], format='mixed', dayfirst=True)
    df['billing_amount'] = pd.to_numeric(df['billing_amount'].astype(str).str.lower().str.strip('rs$£€ '), errors='coerce')
    df['doctor'] = df['doctor'].astype(str).str.strip().str.title()
    df['department'] = df['department'].astype(str).str.strip().str.title()
    
    # To Fill empty strings ONLY for text columns (keeps billing_amount as numeric NaN)
    text_cols = ['patient_name', 'gender', 'follow_up_required', 'doctor', 'department']
    df[text_cols] = df[text_cols].fillna('')
    
    # Export without forced string quotes
    output_uri = f"s3://{dest_bucket}/data/cleaned_clinic_appointments.csv"
    wr.s3.to_csv(df=df, path=output_uri, index=False)
    
    return {'statusCode': 200, 'body': 'ETL Success'}