# Automated AWS Serverless ETL Pipeline: Clinic Data

An advanced, cloud-native evolution of my previous [Clinic-Appointments-Dataset-Cleaning-and-Standardization](https://github.com/yourusername/Clinic-Appointments-Dataset-Cleaning-and-Standardization) project. While the previous iteration successfully established the Pandas logic to clean corrupted primary keys, multi-currency values, and datetime chaos in a local Jupyter Notebook, running local scripts manually is not viable for continuous data engineering. 

This project takes that foundational logic and migrates it entirely to **Amazon Web Services (AWS)** to create a fully automated, event-driven Extract, Transform, and Load (ETL) pipeline. Now, the moment a messy dataset is dropped into an S3 bucket, a serverless compute engine wakes up, standardizes the data, and makes it instantly queryable via distributed SQL, requiring zero human intervention.

---

## Project Highlights & Key Automation Workflow

The workflow is completely decoupled, relying on S3 event triggers, AWS Lambda, and Amazon Athena. Below are the specific architectural techniques and logic implemented:

### 1. Event-Driven Serverless Ingestion (Amazon S3 -> AWS Lambda)
- **Problem**: Manual data pipelines require human triggers or expensive, always-on EC2 servers to monitor for new files.
- **Solution**: 
  * Configured an **S3 `ObjectCreated` Event Notification** on the `clinic-raw-data` bucket.
  * Uploading `messy_clinic_appointments.csv` instantly triggers the `lambda_function.py`, which utilizes the `awswrangler` (AWS Data Wrangler) library to pull the S3 URI directly into a Pandas DataFrame in memory.

### 2. Idempotent Data Load & Storage Routing
- **Problem**: Traditional ETL scripts often "stack" or duplicate data if the pipeline accidentally runs twice on the same file.
- **Solution**: 
  * Engineered **100% idempotency** by hardcoding a fixed output S3 URI (`s3://clinic-processed-data/data/cleaned_messy_clinic_appointments.csv`).
  * Every execution safely *overwrites* the existing processed file instead of appending to it, guaranteeing zero duplicate rows downstream.
  * Separated the `/data/` directory from the `/athena-results/` directory so query logs don't corrupt the analytical tables.

### 3. Serverless Data Transformation (Python & Pandas)
- Carried over and optimized the data cleaning logic from V1 to run in milliseconds within Lambda:
  * **Advanced ID Architecture:** Built collision-proof primary keys using `pd.factorize(df['patient_name'])[0] + 1001`.
  * **Datetime & Currency:** Dynamically parsed mixed dates (`dayfirst=True`) and stripped international currencies (`.str.strip('rs$£€ ')`) coercing them to pure floats.
  * **Strategic Null Handling:** Used `df.fillna('')` exclusively on text columns to prevent empty string quote-wrapping issues in the final CSV export, while leaving numeric missing values as standard `NaN`.

### 4. Advanced Schema Definition & Analytics (Amazon Athena)
- **Problem**: Standard `OpenCSVSerde` parsers in Athena throw fatal Java `NumberFormatException` errors when encountering empty strings (`""`) in numeric columns (like `billing_amount`).
- **Solution**: 
  * Executed a DDL utilizing `LazySimpleSerDe` (`ROW FORMAT DELIMITED`) which natively and gracefully casts missing numeric strings to SQL `NULL` values.
  * Successfully queried the cleansed S3 data lake using complex Presto SQL window functions (e.g., Rolling totals of patients partitioned by department).

---

## Key Technical Insights Learned

1. **IAM Least Privilege**:
   * Scoping the Lambda execution role strictly to `AmazonS3FullAccess` and CloudWatch logging ensures the compute engine cannot maliciously access other AWS services if compromised.
2. **Schema-on-Read Mechanics**:
   * Unlike traditional RDBMS (like MySQL), Athena does not store data. By defining table properties like `"skip.header.line.count"="1"` and pointing to a specific S3 prefix, the SQL engine dynamically projects a schema onto a flat CSV file at query runtime.
3. **The Importance of SerDe Selection**:
   * Choosing the right Serializer/Deserializer (SerDe) is make-or-break in cloud data lakes. Transitioning from OpenCSV to LazySimpleSerDe proved essential for handling imperfect, real-world data without breaking production analytical dashboards.

---

## Pipeline Specifications

| Feature | Architecture / Specification |
| :--- | :--- |
| **Compute Environment** | AWS Lambda (Python 3.11, Pandas, AWS Wrangler Layers) |
| **Storage Infrastructure** | Amazon S3 (Raw Bucket & Processed Bucket) |
| **Query Engine** | Amazon Athena (Presto SQL) |
| **Idempotency** | True (Fixed URI Overwrite) |
| **Automation Latency** | Sub-second (S3 Event Trigger) |

---

## Repository Structure

- `lambda_function.py`: The core Python transformation script deployed on AWS Lambda.
- `Creation Of Table Using Serverless Athena.txt`: The DDL script utilizing `LazySimpleSerDe` to structure the data lake.
- `Rolling Total Of Patients - Query using Athena.txt`: Advanced SQL analytical query used to test the processed data.
- `messy_clinic_appointments.csv`: The original, unstructured input dataset.
- `cleaned_messy_clinic_appointments.csv`: The standardized, processed output dataset generated by Lambda.
- `AWS ETL Visual Execution Log.pdf`: A comprehensive visual document providing step-by-step screenshot proof of S3 triggers, IAM configurations, Lambda logs, and Athena query successes.

---

## Connect with me!
- If you're interested in my work, feel free to reach out!
* [<img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="20" height="20" style="vertical-align:middle"> saideepmacherla](https://www.linkedin.com/in/saideepmacherla)
* [<img src="https://cdn.worldvectorlogo.com/logos/tableau-software.svg" width="20" height="20" style="vertical-align:middle"> Saideep Macherla - Vizzes](https://public.tableau.com/app/profile/saideep.macherla/vizzes)
* [<img src="https://cdn-icons-png.flaticon.com/512/732/732200.png" width="20" height="20" style="vertical-align:middle"> saideepmacherla@gmail.com](mailto:saideepmacherla@gmail.com)
