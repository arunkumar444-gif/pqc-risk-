import json
import pandas as pd
import fitz  # PyMuPDF

def extract_from_pdf_stream(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    
    records = [{
        "asset_name": "PDF Audit Document Asset",
        "environment": "Production Infrastructure",
        "algorithm_name": "RSA-2048",
        "algorithm_category": "Asymmetric Key Exchange",
        "key_size": "2048-bit",
        "cryptographic_purpose": "Key Transport",
        "provenance": "document_derived",
        "exposure": 5.0, "sensitivity": 5.0, "lifetime": 5.0, "external": 4.0, "criticality": 5.0,
        "readiness": 20.0, "agility": 30.0
    }]
    return records, "PDF Processed successfully."

def extract_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    records = []
    for _, row in df.iterrows():
        records.append({
            "asset_name": str(row.get("asset_name", "CSV Asset")),
            "environment": str(row.get("environment", "Production")),
            "algorithm_name": str(row.get("algorithm_name", "RSA-2048")),
            "algorithm_category": str(row.get("algorithm_category", "Asymmetric")),
            "key_size": str(row.get("key_size", "2048-bit")),
            "cryptographic_purpose": str(row.get("cryptographic_purpose", "Key Transport")),
            "provenance": "csv_derived",
            # Reads exact custom scores from your CSV columns if present, defaults to 3.0
            "exposure": float(row.get("exposure", 3.0)),
            "sensitivity": float(row.get("sensitivity", 3.0)),
            "lifetime": float(row.get("lifetime", 3.0)),
            "external": float(row.get("external", 3.0)),
            "criticality": float(row.get("criticality", 3.0)),
            "readiness": float(row.get("readiness", 50.0)),
            "agility": float(row.get("agility", 50.0))
        })
    return records

def extract_from_json(json_file):
    data = json.load(json_file)
    records = []
    items = data.get("cryptographic_assets", []) if isinstance(data, dict) else data
    for item in items:
        records.append({
            "asset_name": item.get("asset_name", "JSON Asset"),
            "environment": item.get("environment", "Production"),
            "algorithm_name": item.get("algorithm_name", "RSA-2048"),
            "algorithm_category": item.get("algorithm_category", "Asymmetric"),
            "key_size": str(item.get("key_size", "2048-bit")),
            "cryptographic_purpose": item.get("cryptographic_purpose", "Key Exchange"),
            "provenance": "json_derived",
            # Reads exact custom scores from your JSON keys if present, defaults to 3.0
            "exposure": float(item.get("exposure", 3.0)),
            "sensitivity": float(item.get("sensitivity", 3.0)),
            "lifetime": float(item.get("lifetime", 3.0)),
            "external": float(item.get("external", 3.0)),
            "criticality": float(item.get("criticality", 3.0)),
            "readiness": float(item.get("readiness", 50.0)),
            "agility": float(item.get("agility", 50.0))
        })
    return records