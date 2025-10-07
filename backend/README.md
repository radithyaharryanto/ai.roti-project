# Vehicle ROI Analysis API

A Flask-based REST API for analyzing Return on Investment (ROI) of vehicles in logistics transportation, powered by Google Gemini AI for intelligent insights generation.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Data Models](#data-models)
- [Customization Guide](#customization-guide)
- [Error Handling](#error-handling)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Features

- **Comprehensive ROI Analysis**: Calculate and categorize vehicle investment returns
- **TCO (Total Cost of Ownership) Analysis**: Break down ownership vs operational costs
- **Break-Even Point Calculation**: Determine payback period in years and kilometers
- **Contribution Margin Analysis**: Analyze profit margins per kilometer
- **AI-Powered Insights**: Generate intelligent business recommendations using Google Gemini
- **Dynamic Risk Assessment**: Automatic warnings based on predefined business rules
- **Structured JSON Output**: Frontend-ready data format
- **Indonesian Localization**: Currency formatting and language support

## Prerequisites

- Python 3.7+
- Google Gemini API Key
- Flask and related dependencies

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd vehicle-roi-analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-cors google-generativeai python-dotenv
   ```

## Configuration

1. **Create environment file**
   ```bash
   touch .env
   ```

2. **Add your API key to `.env`**
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Get Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste it into your `.env` file

## API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "language": "Indonesian",
  "output_format": "Structured JSON",
  "endpoints": {
    "/health": "Health check endpoint",
    "/analyze": "Vehicle ROI analysis endpoint"
  }
}
```

#### 2. Analyze Vehicle ROI
```http
POST /analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "unit_name": "Toyota Hiace",
  "segment": "Commercial Van",
  "unit_price": 450000000,
  "uses_leasing": false,
  "tco": 1200000000,
  "annual_tco": 240000000,
  "cost_per_km": 5000,
  "revenue_per_km": 7500,
  "contribution_margin": 2500,
  "total_revenue": 300000000,
  "roi": 1.25,
  "bep_years": 2.5,
  "bep_km": 150000,
  "owning_pct": 0.60,
  "operational_pct": 0.40,
  "residual_value_pct": 0.30
}
```

**Response Structure:**
```json
{
  "roi": {
    "percentage": "125.0%",
    "category": "Layak",
    "short_sentence": "...",
    "insight_narrative": "..."
  },
  "tco": {
    "amount_rp": "Rp 5.000",
    "category": "Efisien",
    "short_sentence": "...",
    "insight_narrative": "..."
  },
  "owning_vs_operational": {
    "owning_percentage": 60,
    "operational_percentage": 40,
    "category": "Owning Dominan",
    "short_sentence": "...",
    "cashflow_implication": "...",
    "pie_chart_data": {
      "owning_cost": 60,
      "operational_cost": 40
    }
  },
  "break_even_point": {
    "period": "2 tahun 6 bulan",
    "bep_km": "150.000 km",
    "category": "Cepat",
    "short_sentence": "...",
    "monthly_simulation": {
      "installment": "...",
      "revenue": "...",
      "net_cashflow": "..."
    },
    "bep_insight": "..."
  },
  "contribution_margin_per_km": {
    "margin_rp": "Rp 2.500",
    "category": "Rendah",
    "short_sentence": "...",
    "margin_insight": "..."
  },
  "overall_insight": {
    "summary": "..."
  }
}
```

## Data Models

### Input Data Model (VehicleInputData)

| Field                 | Type    | Required | Description                               |
| --------------------- | ------- | -------- | ----------------------------------------- |
| `unit_name`           | string  | Yes      | Vehicle unit name                         |
| `segment`             | string  | Yes      | Vehicle segment/category                  |
| `unit_price`          | float   | Yes      | Vehicle purchase price                    |
| `uses_leasing`        | boolean | No       | Whether using leasing option              |
| `tco`                 | float   | Yes      | Total Cost of Ownership                   |
| `annual_tco`          | float   | Yes      | Annual TCO                                |
| `cost_per_km`         | float   | Yes      | Cost per kilometer                        |
| `revenue_per_km`      | float   | Yes      | Revenue per kilometer                     |
| `contribution_margin` | float   | Yes      | Contribution margin per km                |
| `total_revenue`       | float   | Yes      | Total expected revenue                    |
| `roi`                 | float   | Yes      | Return on Investment ratio                |
| `bep_years`           | float   | Yes      | Break-even point in years                 |
| `bep_km`              | float   | Yes      | Break-even point in kilometers            |
| `owning_pct`          | float   | No       | Owning cost percentage (0-1)              |
| `operational_pct`     | float   | No       | Operational cost percentage (0-1)         |
| `residual_value_pct`  | float   | No       | Residual value percentage (default: 0.30) |

## Customization Guide

### 1. Modifying Categorization Rules

Edit the `categorization_rules` in the `VehicleROIAnalyzer` class:

```python
self.categorization_rules = {
    "roi_score": [
        {"label": "Custom Category", "criteria": lambda roi: roi > 2.0, "quick_message": "Your custom message"},
        # Add more categories...
    ],
    # Modify other categories...
}
```

### 2. Adding New Analysis Metrics

**Step 1:** Add field to `VehicleInputData`:
```python
@dataclass
class VehicleInputData:
    # existing fields...
    new_metric: float = 0
```

**Step 2:** Add validation in `validate_vehicle_data()`:
```python
new_metric = data.get('new_metric')
if new_metric is not None and not isinstance(new_metric, (int, float)):
    errors.append("new_metric must be a number")
```

**Step 3:** Create analysis method:
```python
def analyze_new_metric(self, value: float) -> Dict[str, str]:
    # Your analysis logic here
    return {"category": "...", "insight": "..."}
```

**Step 4:** Add to `process_vehicle_data()`:
```python
analysis["new_metric_analysis"] = self.analyze_new_metric(data.new_metric)
```

### 3. Customizing Dynamic Warnings

Modify `evaluate_dynamic_conditions()` method:

```python
def evaluate_dynamic_conditions(self, data: VehicleInputData) -> List[str]:
    warnings = []
    
    # Add your custom conditions
    if data.your_custom_field > threshold:
        warnings.append("Your custom warning message")
    
    return warnings
```

### 4. Changing AI Model or Prompt

**Switch AI Provider:**
```python
# Replace Gemini with OpenAI
import openai
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In generate_structured_analysis():
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
```

**Customize AI Prompt:**
Edit the `prompt` variable in `generate_structured_analysis()` to change:
- Analysis depth
- Output format
- Language/tone
- Business focus areas

### 5. Adding New Output Fields

**Step 1:** Extend output dataclasses:
```python
@dataclass
class NewAnalysis:
    value: str
    category: str
    insight: str

@dataclass
class VehicleROIOutput:
    # existing fields...
    new_analysis: NewAnalysis
```

**Step 2:** Update AI prompt to include new field in JSON structure

### 6. Localization Changes

**Change Currency Format:**
```python
def format_currency(self, value: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f"${value:,.2f}"
    elif currency == "EUR":
        return f"€{value:,.2f}"
    # Add more currencies...
```

**Change Language:**
- Modify category labels in `categorization_rules`
- Update AI prompt language
- Change date/number formatting

### 7. Adding Database Integration

```python
from sqlalchemy import create_engine
from your_models import VehicleAnalysis

@app.route('/analyze', methods=['POST'])
def analyze_vehicle_roi():
    # ... existing code ...
    
    # Save to database
    analysis_record = VehicleAnalysis(
        vehicle_name=validated_data.unit_name,
        roi_result=response_data,
        created_at=datetime.now()
    )
    db.session.add(analysis_record)
    db.session.commit()
    
    return jsonify(response_data)
```

### 8. Adding Authentication

```python
from functools import wraps
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Token invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/analyze', methods=['POST'])
@token_required
def analyze_vehicle_roi():
    # ... existing code ...
```

## Error Handling

The API handles several types of errors:

- **400 Bad Request**: Invalid input data or validation errors
- **500 Internal Server Error**: Processing or AI generation failures
- **Missing API Key**: Environment configuration errors

Example error response:
```json
{
  "error": "Validasi data gagal",
  "details": "unit_name is required and cannot be empty, roi must be a positive number"
}
```

## Development

### Running in Development Mode

```bash
python app.py
```

The server will start on `http://localhost:5000` with auto-reload enabled.

### Testing the API

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

### Environment Variables

| Variable         | Description                                | Required |
| ---------------- | ------------------------------------------ | -------- |
| `GEMINI_API_KEY` | Google Gemini API key                      | Yes      |
| `FLASK_ENV`      | Flask environment (development/production) | No       |
| `PORT`           | Server port (default: 5000)                | No       |

## Deployment

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  vehicle-roi-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

### Production Considerations

1. **Use Production WSGI Server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set Production Environment:**
   ```python
   app.config['ENV'] = 'production'
   app.config['DEBUG'] = False
   ```

3. **Add Rate Limiting:**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   
   @app.route('/analyze', methods=['POST'])
   @limiter.limit("100 per hour")
   def analyze_vehicle_roi():
       # ... existing code ...
   ```

4. **Add Logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Create an issue in the repository
- Check the API documentation
- Review the customization guide above

---

**Note**: This API requires a valid Google Gemini API key. Make sure to keep your API key secure and never commit it to version control.