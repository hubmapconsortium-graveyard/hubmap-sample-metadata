local metadata = import '../inputs/metadata.json';

{
    "file_core": {
        "file_name": "clinical-data.txt",
        "format": "txt"
    },
    "provenance": {
        "document_id": metadata.document_id,
        "submission_date": metadata.submission_date
    },
    "file_description": "Clinicial data export",
    "schema_type": "file",
    "describedBy": "https://schema.humancellatlas.org/type/file/2.2.0/supplementary_file"
}
