# PDF Extractor Service

A Python service using PDF-plumber for superior PDF text extraction, specifically optimized for real estate documents.

## Features

- **Superior text extraction** using PDF-plumber
- **Table extraction** for structured content
- **Form field handling** for real estate documents
- **Line number filtering** to remove artifacts
- **Layout preservation** for better text quality
- **RESTful API** with Flask

## Installation

1. **Install Python dependencies:**
```bash
cd python_services
pip install -r requirements.txt
```

2. **Run the service:**
```bash
python pdf_extractor.py
```

The service will start on `http://localhost:5001`

## API Endpoints

### Health Check
```
GET /health
```

### Extract PDF (File Upload)
```
POST /extract
Content-Type: multipart/form-data
Body: file (PDF file)
```

### Extract PDF (Base64)
```
POST /extract-base64
Content-Type: application/json
Body: {"pdf_data": "base64_encoded_pdf"}
```

## Response Format

```json
{
  "success": true,
  "text": "Extracted text content...",
  "page_count": 3,
  "pages": ["Page 1 text", "Page 2 text", "Page 3 text"],
  "method": "pdfplumber",
  "confidence": 0.95
}
```

## Environment Variables

- `PORT`: Service port (default: 5001)
- `DEBUG`: Enable debug mode (default: false)

## Integration

The Node.js application calls this service via HTTP requests for PDF text extraction.
