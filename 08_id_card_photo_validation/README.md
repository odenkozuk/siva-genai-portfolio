# ID Card Photo Validation Pipeline

Automated employee ID card photo validation using **Azure Face API** and **Azure Computer Vision API**. Validates background color, image dimensions, face orientation, blur, and compliance — reducing manual validation effort by **~70%** and improving onboarding compliance accuracy.

---

## Overview

Employee onboarding requires ID card photos to meet strict standards (white background, forward-facing, minimum resolution, single face). Manual review of hundreds of photos per month is slow and inconsistent. This pipeline automates the entire validation process and auto-flags non-compliant photos before ID card printing.

---

## Architecture

```
Input Photo (JPG/PNG)
     │
     ▼
Dimension Validator
     │  Width, height, aspect ratio check
     ▼
Background Validator
     │  Border pixel brightness sampling (white background check)
     ▼
Azure Face API
     │  Face detection, head pose (roll/yaw), blur, occlusion
     ▼
ValidationResult (compliant: true/false, violations: [...])
     │
     ├──► Compliant  → Approved for ID card printing
     └──► Violations → Auto-flagged with specific reasons
               │
               ▼
         CSV Validation Report
```

---

## Validation Rules

| Check | Standard |
|-------|----------|
| Minimum resolution | 400 × 400 px |
| Maximum resolution | 2000 × 2000 px |
| Aspect ratio | 0.75 to 1.33 (portrait/square) |
| Background brightness | ≥ 200/255 (white/light background) |
| Face detected | Exactly 1 face required |
| Head roll (tilt) | ≤ 10 degrees |
| Head yaw (turn) | ≤ 15 degrees |
| Image blur | Must not be High blur |
| Face coverage | ≥ 15% of total image area |

---

## Features

- **Dimension and aspect ratio** validation via Pillow
- **Background brightness** check using border pixel sampling (no API cost)
- **Azure Face API** — face detection, head pose estimation, blur level
- **Multi-face detection** — flags photos with more than one face
- **Batch processing** — validates an entire directory, saves CSV report
- **Detailed violations** — specific, human-readable reasons for non-compliance
- **Single-photo mode** — validate one image from CLI

---

## Project Structure

```
08_id_card_photo_validation/
├── src/
│   └── photo_validator.py    # Full validation pipeline
├── data/
│   ├── input/                # Place photos here for batch validation
│   └── output/               # validation_report.csv saved here
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `AZURE_FACE_API_KEY` | Azure Face API key |
| `AZURE_FACE_ENDPOINT` | Azure Face API endpoint |
| `AZURE_VISION_API_KEY` | Azure Computer Vision API key |
| `AZURE_VISION_ENDPOINT` | Azure Computer Vision endpoint |
| `INPUT_DIR` | Directory containing photos to validate |
| `OUTPUT_DIR` | Directory for the CSV validation report |

### 3. Provision Azure Resources

```bash
# Create Face API resource
az cognitiveservices account create \
  --name face-validator \
  --resource-group myRG \
  --kind Face \
  --sku S0 \
  --location eastus

# Create Computer Vision resource
az cognitiveservices account create \
  --name vision-validator \
  --resource-group myRG \
  --kind ComputerVision \
  --sku S1 \
  --location eastus
```

---

## Usage

### Validate a single photo

```bash
python src/photo_validator.py data/input/employee_photo.jpg
```

Output:
```json
{
  "file": "employee_photo.jpg",
  "compliant": false,
  "violations": [
    "Head tilt too large: 14.3° (max 10°)",
    "Background too dark (brightness 142/255, min 200)"
  ]
}
```

### Batch validate a directory

```python
from src.photo_validator import batch_validate

report = batch_validate(
    input_dir="data/input",
    output_dir="data/output"
)
# Saves data/output/validation_report.csv
```

### Programmatic single validation

```python
from src.photo_validator import validate_photo

result = validate_photo("data/input/photo.jpg")
if result.is_compliant:
    print("Photo approved.")
else:
    for violation in result.violations:
        print(f"  - {violation}")
```

---

## CSV Report Format

The batch report (`validation_report.csv`) contains:

| Column | Description |
|--------|-------------|
| `file` | Photo filename |
| `compliant` | True / False |
| `violations` | Semicolon-separated list of violations |
| `face_detected` | Whether a face was found |
| `dimensions` | Image resolution (e.g. `800x800`) |
| `head_roll` | Head tilt in degrees |
| `head_yaw` | Head turn in degrees |
| `background_brightness` | Average border brightness (0–255) |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Face Detection | Azure Face API |
| Image Analysis | Azure Computer Vision API |
| Image Processing | Pillow (PIL) |
| Auth | Azure Cognitive Services Credentials |
| Output | CSV via Python csv module |
| Language | Python 3.12 |

---

## Results

- **~70% reduction** in manual photo review effort
- Consistent validation across all submissions (no reviewer fatigue)
- Auto-flags non-compliant photos before ID card printing
- Specific violation messages reduce re-submission cycles
