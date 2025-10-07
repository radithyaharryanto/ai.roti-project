# Import required libraries for web framework, AI integration, and environment management
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import locale
import json
from dataclasses import dataclass, asdict

# Load environment variables from .env file
load_dotenv()

# Initialize Flask web application
app = Flask(__name__)
CORS(app)

# Configure Gemini AI client with API key from environment variables
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Try to set Indonesian locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except:
        pass

# Input Data Models
@dataclass
class VehicleInputData:
    """Input data structure for vehicle ROI analysis"""
    unit_name: str
    segment: str
    unit_price: float
    uses_leasing: bool = False
    tco: float = 0
    annual_tco: float = 0
    cost_per_km: float = 0
    revenue_per_km: float = 0
    contribution_margin: float = 0
    total_revenue: float = 0
    roi: float = 0
    bep_years: float = 0
    bep_km: float = 0
    owning_pct: float = 0.0
    operational_pct: float = 0.0
    residual_value_pct: float = 0.30

def validate_vehicle_data(data: dict) -> VehicleInputData:
    """Validate input data and return VehicleInputData instance"""
    errors = []
    
    # Required string fields
    unit_name = data.get('unit_name', '').strip()
    if not unit_name:
        errors.append("unit_name is required and cannot be empty")
    
    segment = data.get('segment', '').strip()
    if not segment:
        errors.append("segment is required and cannot be empty")
    
    # Required positive float fields
    required_positive_fields = [
        'unit_price', 'tco', 'annual_tco', 'cost_per_km', 
        'revenue_per_km', 'contribution_margin', 'total_revenue', 
        'roi', 'bep_years', 'bep_km'
    ]
    
    for field in required_positive_fields:
        value = data.get(field)
        if value is None:
            errors.append(f"{field} is required")
        elif not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{field} must be a positive number")
    
    # Percentage fields (0-1 range)
    percentage_fields = ['owning_pct', 'operational_pct', 'residual_value_pct']
    for field in percentage_fields:
        value = data.get(field)
        if value is not None:
            if not isinstance(value, (int, float)) or not (0 <= value <= 1):
                errors.append(f"{field} must be between 0 and 1")
    
    # Boolean field
    uses_leasing = data.get('uses_leasing', False)
    if not isinstance(uses_leasing, bool):
        errors.append("uses_leasing must be a boolean")
    
    if errors:
        raise ValueError(f"Validation errors: {', '.join(errors)}")
    
    return VehicleInputData(
        unit_name=unit_name,
        segment=segment,
        unit_price=float(data['unit_price']),
        uses_leasing=bool(uses_leasing),
        tco=float(data['tco']),
        annual_tco=float(data['annual_tco']),
        cost_per_km=float(data['cost_per_km']),
        revenue_per_km=float(data['revenue_per_km']),
        contribution_margin=float(data['contribution_margin']),
        total_revenue=float(data['total_revenue']),
        roi=float(data['roi']),
        bep_years=float(data['bep_years']),
        bep_km=float(data['bep_km']),
        owning_pct=float(data.get('owning_pct', 0.0)),
        operational_pct=float(data.get('operational_pct', 0.0)),
        residual_value_pct=float(data.get('residual_value_pct', 0.30))
    )

# Output Data Models
@dataclass
class ROIAnalysis:
    percentage: str
    category: str
    short_sentence: str
    insight_narrative: str

@dataclass
class TCOAnalysis:
    amount_rp: str
    category: str
    short_sentence: str
    insight_narrative: str

@dataclass
class PieChartData:
    owning_cost: int
    operational_cost: int

@dataclass
class OwningVsOperational:
    owning_percentage: int
    operational_percentage: int
    category: str
    short_sentence: str
    cashflow_implication: str
    pie_chart_data: PieChartData

@dataclass
class MonthlySimulation:
    installment: str
    revenue: str
    net_cashflow: str

@dataclass
class BreakEvenPoint:
    period: str
    bep_km: str
    category: str
    short_sentence: str
    monthly_simulation: MonthlySimulation
    bep_insight: str

@dataclass
class ContributionMargin:
    margin_rp: str
    category: str
    short_sentence: str
    margin_insight: str

@dataclass
class OverallInsight:
    summary: str

@dataclass
class VehicleROIOutput:
    roi: ROIAnalysis
    tco: TCOAnalysis
    owning_vs_operational: OwningVsOperational
    break_even_point: BreakEvenPoint
    contribution_margin_per_km: ContributionMargin
    overall_insight: OverallInsight

class VehicleROIAnalyzer:
    """Analis ROI kendaraan untuk transportasi logistik"""
    
    def __init__(self):
        self.categorization_rules = {
            "roi_score": [
                {"label": "Sangat Layak", "criteria": lambda roi: roi > 1.5, "quick_message": "Pengembalian luar biasa di atas standar industri"},
                {"label": "Layak", "criteria": lambda roi: 1.0 < roi <= 1.5, "quick_message": "Investasi sehat dengan margin memadai"},
                {"label": "Perlu Dievaluasi", "criteria": lambda roi: 0.7 < roi <= 1.0, "quick_message": "Profit tipis dan sensitif terhadap fluktuasi"},
                {"label": "Tidak Disarankan", "criteria": lambda roi: 0.5 < roi <= 0.7, "quick_message": "Pengembalian rendah dan berisiko"},
                {"label": "Rugi", "criteria": lambda roi: roi <= 0.5, "quick_message": "Berpotensi rugi signifikan"}
            ],
            "cost_per_km": [
                {"label": "Sangat Efisien", "min": 0, "max": 4800, "quick_message": "Biaya sangat rendah, keunggulan kompetitif"},
                {"label": "Efisien", "min": 4801, "max": 5200, "quick_message": "Biaya kompetitif, aman untuk profit"},
                {"label": "Kurang Efisien", "min": 5201, "max": 5500, "quick_message": "Biaya mulai menekan margin"},
                {"label": "Tidak Efisien", "min": 5501, "max": float('inf'), "quick_message": "Biaya tinggi, kurang kompetitif"}
            ],
            "bep_years": [
                {"label": "Sangat Cepat", "criteria": lambda bep: bep <= 2, "quick_message": "Balik modal sangat cepat"},
                {"label": "Cepat", "criteria": lambda bep: 2 < bep <= 3, "quick_message": "Waktu impas kompetitif"},
                {"label": "Lambat", "criteria": lambda bep: 3 < bep <= 4, "quick_message": "Balik modal lama"},
                {"label": "Sangat Lambat", "criteria": lambda bep: bep > 4, "quick_message": "Balik modal terlalu lama"}
            ],
            "contribution_margin": [
                {"label": "Sangat Tinggi", "criteria": lambda margin: margin >= 6000, "quick_message": "Margin kuat dan tahan fluktuasi"},
                {"label": "Tinggi", "criteria": lambda margin: 5500 <= margin < 6000, "quick_message": "Margin sehat dan stabil"},
                {"label": "Cukup", "criteria": lambda margin: 5000 <= margin < 5500, "quick_message": "Margin moderat"},
                {"label": "Rendah", "criteria": lambda margin: margin < 5000, "quick_message": "Margin tipis"}
            ],
            "structure_cost": [
                {"label": "Seimbang", "criteria": lambda owning: 0.40 <= owning <= 0.60, "quick_message": "Struktur sehat"},
                {"label": "Owning Dominan", "criteria": lambda owning: owning > 0.60, "quick_message": "CAPEX berat"},
                {"label": "Operational Dominan", "criteria": lambda owning: owning < 0.40, "quick_message": "OPEX berat"}
            ]
        }

    def format_currency(self, value: float) -> str:
        """Format nilai mata uang dalam format Indonesia"""
        try:
            return f"Rp {value:,.0f}".replace(',', '.')
        except:
            return f"Rp {int(value):,}".replace(',', '.')

    def format_percentage(self, value: float, decimals: int = 1) -> str:
        """Format persentase"""
        return f"{value * 100:.{decimals}f}%"

    def format_bep_years(self, bep_years: float) -> str:
        """Konversi BEP years ke format [tahun, bulan]"""
        years = int(bep_years)
        months = round((bep_years - years) * 12)
        if months == 12:
            years += 1
            months = 0
        
        if years == 0:
            return f"{months} bulan"
        elif months == 0:
            return f"{years} tahun"
        else:
            return f"{years} tahun {months} bulan"

    def categorize_roi(self, roi: float) -> Dict[str, str]:
        """Kategorisasi ROI"""
        for category in self.categorization_rules["roi_score"]:
            if category["criteria"](roi):
                return {"label": category["label"], "message": category["quick_message"]}
        return {"label": "Tidak Terkategori", "message": "ROI tidak dapat dikategorikan"}

    def categorize_cost_per_km(self, cost: float) -> Dict[str, str]:
        """Kategorisasi biaya per km"""
        for category in self.categorization_rules["cost_per_km"]:
            if category["min"] <= cost <= category["max"]:
                return {"label": category["label"], "message": category["quick_message"]}
        return {"label": "Tidak Terkategori", "message": "Biaya tidak dapat dikategorikan"}

    def categorize_bep(self, bep_years: float) -> Dict[str, str]:
        """Kategorisasi break even point"""
        for category in self.categorization_rules["bep_years"]:
            if category["criteria"](bep_years):
                return {"label": category["label"], "message": category["quick_message"]}
        return {"label": "Tidak Terkategori", "message": "BEP tidak dapat dikategorikan"}

    def categorize_contribution_margin(self, margin: float) -> Dict[str, str]:
        """Kategorisasi contribution margin"""
        for category in self.categorization_rules["contribution_margin"]:
            if category["criteria"](margin):
                return {"label": category["label"], "message": category["quick_message"]}
        return {"label": "Tidak Terkategori", "message": "Margin tidak dapat dikategorikan"}

    def categorize_cost_structure(self, owning_pct: float) -> Dict[str, str]:
        """Kategorisasi struktur biaya"""
        for category in self.categorization_rules["structure_cost"]:
            if category["criteria"](owning_pct):
                return {"label": category["label"], "message": category["quick_message"]}
        return {"label": "Tidak Terkategori", "message": "Struktur tidak dapat dikategorikan"}

    def evaluate_dynamic_conditions(self, data: VehicleInputData) -> List[str]:
        """Evaluasi kondisi dinamis berdasarkan rules dari prompt"""
        warnings = []
        
        # ROI < 1.0 → Tambahkan catatan evaluasi profitabilitas
        if data.roi < 1.0:
            warnings.append("Evaluasi Profitabilitas: ROI di bawah 100% menunjukkan investasi tidak menguntungkan. Pertimbangkan revisi strategi pricing atau efisiensi operasional.")
        
        # BEP > 3 tahun → Catatan risiko durasi balik modal
        if data.bep_years > 3:
            warnings.append("Risiko Durasi Balik Modal: Break-even point lebih dari 3 tahun meningkatkan eksposur risiko pasar dan teknologi. Evaluasi skenario worst-case.")
        
        # Margin < 5000 → Catatan risiko ketahanan profit
        if data.contribution_margin < 5000:
            warnings.append("Risiko Ketahanan Profit: Margin kontribusi rendah membuat bisnis rentan terhadap fluktuasi biaya operasional dan kompetisi harga.")
        
        # Owning > 65% → Catatan opsi leasing/perpanjangan masa pakai
        if data.owning_pct > 0.65:
            warnings.append("Optimasi Struktur Modal: Owning cost dominan (>65%) - pertimbangkan opsi leasing atau perpanjangan masa pakai untuk mengurangi beban CAPEX.")
        
        # Cost per KM > 5500 → Catatan tinjauan efisiensi
        if data.cost_per_km > 5500:
            warnings.append("Tinjauan Efisiensi: Biaya per km tinggi (>Rp 5.500) memerlukan audit operasional untuk identifikasi area penghematan biaya.")
        
        # Revenue per KM < 7000 → Catatan tarif pasar/segmen
        if data.revenue_per_km < 7000:
            warnings.append("Evaluasi Tarif: Revenue per km rendah (<Rp 7.000) - analisis kompetitif pricing dan potensi segmen premium diperlukan.")
        
        # TCO > 1.5 miliar → Catatan pastikan premiumnya terbayar oleh revenue
        if data.tco > 1500000000:  # 1.5 miliar
            warnings.append("Validasi Premium Investment: TCO tinggi (>Rp 1.5M) memerlukan justifikasi premium melalui revenue superior atau efisiensi operasional yang terbukti.")
        
        return warnings

    def process_vehicle_data(self, data: VehicleInputData) -> Dict[str, Any]:
        """Proses data kendaraan dan buat analisis terstruktur"""
        analysis = {
            "unit_info": {
                "name": data.unit_name,
                "segment": data.segment,
                "price": self.format_currency(data.unit_price),
                "uses_leasing": data.uses_leasing
            }
        }

        # ROI Analysis
        roi_category = self.categorize_roi(data.roi)
        analysis["roi_analysis"] = {
            "value": self.format_percentage(data.roi, 1),
            "category": roi_category["label"],
            "insight": roi_category["message"]
        }

        # TCO Analysis
        cost_category = self.categorize_cost_per_km(data.cost_per_km)
        analysis["tco_analysis"] = {
            "total": self.format_currency(data.tco),
            "annual": self.format_currency(data.annual_tco),
            "per_km": self.format_currency(data.cost_per_km),
            "efficiency": cost_category["label"],
            "insight": cost_category["message"]
        }

        # Cost Structure Analysis
        structure_category = self.categorize_cost_structure(data.owning_pct)
        analysis["cost_structure"] = {
            "owning_percentage": self.format_percentage(data.owning_pct, 0),
            "operational_percentage": self.format_percentage(data.operational_pct, 0),
            "structure_type": structure_category["label"],
            "insight": structure_category["message"]
        }

        # Break Even Point Analysis
        bep_category = self.categorize_bep(data.bep_years)
        analysis["bep_analysis"] = {
            "years_formatted": self.format_bep_years(data.bep_years),
            "kilometers": f"{data.bep_km:,.0f} km".replace(',', '.'),
            "category": bep_category["label"],
            "insight": bep_category["message"]
        }

        # Contribution Margin Analysis
        margin_category = self.categorize_contribution_margin(data.contribution_margin)
        analysis["margin_analysis"] = {
            "per_km": self.format_currency(data.contribution_margin),
            "revenue_per_km": self.format_currency(data.revenue_per_km),
            "total_revenue": self.format_currency(data.total_revenue),
            "category": margin_category["label"],
            "insight": margin_category["message"]
        }

        # Dynamic Conditions Evaluation
        analysis["dynamic_warnings"] = self.evaluate_dynamic_conditions(data)

        return analysis

def generate_structured_analysis(analysis_data: Dict[str, Any], raw_data: VehicleInputData) -> VehicleROIOutput:
    """Generate structured analysis for frontend consumption using Google Gemini"""
    
    # Format dynamic warnings for the prompt
    warnings_text = ""
    if analysis_data.get('dynamic_warnings'):
        warnings_text = " " + " ".join([warning.replace(":", " -") for warning in analysis_data['dynamic_warnings']])
    
    prompt = f"""Generate JSON summary for vehicle performance metrics IN INDONESIAN LANGUAGE.

Vehicle: {analysis_data['unit_info']['name']} ({analysis_data['unit_info']['segment']})
ROI: {analysis_data['roi_analysis']['value']} - {analysis_data['roi_analysis']['category']}
Cost/KM: {analysis_data['tco_analysis']['per_km']} - {analysis_data['tco_analysis']['efficiency']}
Cost Structure: {analysis_data['cost_structure']['structure_type']}
BEP: {analysis_data['bep_analysis']['years_formatted']} - {analysis_data['bep_analysis']['category']}
Margin: {analysis_data['margin_analysis']['per_km']} - {analysis_data['margin_analysis']['category']}{warnings_text}

Return JSON with all text fields in Bahasa Indonesia:

{{
  "roi": {{
    "percentage": "{analysis_data['roi_analysis']['value']}",
    "category": "{analysis_data['roi_analysis']['category']}",
    "short_sentence": "Ringkasan singkat hasil ROI dalam bahasa Indonesia",
    "insight_narrative": "Penjelasan lengkap kinerja ROI dalam bahasa Indonesia"
  }},
  "tco": {{
    "amount_rp": "{analysis_data['tco_analysis']['per_km']}",
    "category": "{analysis_data['tco_analysis']['efficiency']}",
    "short_sentence": "Ringkasan efisiensi biaya dalam bahasa Indonesia",
    "insight_narrative": "Analisis detail biaya per km dalam bahasa Indonesia"
  }},
  "owning_vs_operational": {{
    "owning_percentage": {int(raw_data.owning_pct * 100)},
    "operational_percentage": {int(raw_data.operational_pct * 100)},
    "category": "{analysis_data['cost_structure']['structure_type']}",
    "short_sentence": "Ringkasan komposisi biaya dalam bahasa Indonesia",
    "cashflow_implication": "Analisis dampak arus kas dalam bahasa Indonesia",
    "pie_chart_data": {{
      "owning_cost": {int(raw_data.owning_pct * 100)},
      "operational_cost": {int(raw_data.operational_pct * 100)}
    }}
  }},
  "break_even_point": {{
    "period": "{analysis_data['bep_analysis']['years_formatted']}",
    "bep_km": "{analysis_data['bep_analysis']['kilometers']}",
    "category": "{analysis_data['bep_analysis']['category']}",
    "short_sentence": "Ringkasan periode balik modal dalam bahasa Indonesia",
    "monthly_simulation": {{
      "installment": "Estimasi cicilan bulanan dalam bahasa Indonesia",
      "revenue": "Estimasi pendapatan bulanan dalam bahasa Indonesia",
      "net_cashflow": "Estimasi arus kas bersih dalam bahasa Indonesia"
    }},
    "bep_insight": "Analisis dan timeline balik modal dalam bahasa Indonesia"
  }},
  "contribution_margin_per_km": {{
    "margin_rp": "{analysis_data['margin_analysis']['per_km']}",
    "category": "{analysis_data['margin_analysis']['category']}",
    "short_sentence": "Ringkasan margin dalam bahasa Indonesia",
    "margin_insight": "Analisis margin per kilometer dalam bahasa Indonesia"
  }},
  "overall_insight": {{
    "summary": "Ringkasan keseluruhan semua metrik dalam bahasa Indonesia"
  }}
}}"""

    try:
        # Define safety settings
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Generate content using Gemini with JSON mode
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=8192,
                temperature=0.5,
                response_mime_type="application/json",
            ),
            safety_settings=safety_settings
        )
        
        # Check if response is valid before accessing text
        if not response.candidates or not response.candidates[0].content.parts:
            print("--- GEMINI BLOCKED RESPONSE ---")
            print(f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
            print("Prompt length:", len(prompt))
            print("--- END DEBUG ---")
            # Use fallback instead of raising error
            raise ValueError("Gemini response was blocked by safety filters")
        
        # Extract the AI's response and parse as JSON
        response_text = response.text.strip()

        # Try to extract JSON from the response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text
        
        # Parse JSON response with better error handling
        try:
            raw_json = json.loads(json_text)
        except json.JSONDecodeError as e:
            print("--- JSON PARSING ERROR ---")
            print(f"Error: {e}")
            print(f"Response text (first 500 chars): {response_text[:500]}")
            print("--- END ERROR ---")
            raise
        
        # Add missing fields if not present in AI response
        if "owning_vs_operational" in raw_json and "pie_chart_data" not in raw_json["owning_vs_operational"]:
            raw_json["owning_vs_operational"]["pie_chart_data"] = {
                "owning_cost": raw_json["owning_vs_operational"]["owning_percentage"],
                "operational_cost": raw_json["owning_vs_operational"]["operational_percentage"]
            }
        
        # Convert to structured dataclasses
        structured_data = VehicleROIOutput(
            roi=ROIAnalysis(**raw_json["roi"]),
            tco=TCOAnalysis(**raw_json["tco"]),
            owning_vs_operational=OwningVsOperational(
                owning_percentage=raw_json["owning_vs_operational"]["owning_percentage"],
                operational_percentage=raw_json["owning_vs_operational"]["operational_percentage"],
                category=raw_json["owning_vs_operational"]["category"],
                short_sentence=raw_json["owning_vs_operational"]["short_sentence"],
                cashflow_implication=raw_json["owning_vs_operational"]["cashflow_implication"],
                pie_chart_data=PieChartData(**raw_json["owning_vs_operational"]["pie_chart_data"])
            ),
            break_even_point=BreakEvenPoint(
                period=raw_json["break_even_point"]["period"],
                bep_km=raw_json["break_even_point"]["bep_km"],
                category=raw_json["break_even_point"]["category"],
                short_sentence=raw_json["break_even_point"]["short_sentence"],
                monthly_simulation=MonthlySimulation(**raw_json["break_even_point"]["monthly_simulation"]),
                bep_insight=raw_json["break_even_point"]["bep_insight"]
            ),
            contribution_margin_per_km=ContributionMargin(**raw_json["contribution_margin_per_km"]),
            overall_insight=OverallInsight(**raw_json["overall_insight"])
        )
        
        return structured_data
    
    except Exception as e:
        # Return fallback structure if AI call fails
        return VehicleROIOutput(
            roi=ROIAnalysis(
                percentage=analysis_data['roi_analysis']['value'],
                category=analysis_data['roi_analysis']['category'],
                short_sentence=analysis_data['roi_analysis']['insight'],
                insight_narrative="Error dalam menghasilkan insight AI. Menggunakan analisis fallback."
            ),
            tco=TCOAnalysis(
                amount_rp=analysis_data['tco_analysis']['per_km'],
                category=analysis_data['tco_analysis']['efficiency'],
                short_sentence=analysis_data['tco_analysis']['insight'],
                insight_narrative="Error dalam menghasilkan insight AI. Menggunakan analisis fallback."
            ),
            owning_vs_operational=OwningVsOperational(
                owning_percentage=int(raw_data.owning_pct * 100),
                operational_percentage=int(raw_data.operational_pct * 100),
                category=analysis_data['cost_structure']['structure_type'],
                short_sentence=analysis_data['cost_structure']['insight'],
                cashflow_implication="Error dalam menghasilkan insight AI. Menggunakan analisis fallback.",
                pie_chart_data=PieChartData(
                    owning_cost=int(raw_data.owning_pct * 100),
                    operational_cost=int(raw_data.operational_pct * 100)
                )
            ),
            break_even_point=BreakEvenPoint(
                period=analysis_data['bep_analysis']['years_formatted'],
                bep_km=analysis_data['bep_analysis']['kilometers'],
                category=analysis_data['bep_analysis']['category'],
                short_sentence=analysis_data['bep_analysis']['insight'],
                monthly_simulation=MonthlySimulation(
                    installment="Tidak tersedia",
                    revenue="Tidak tersedia",
                    net_cashflow="Tidak tersedia"
                ),
                bep_insight="Error dalam menghasilkan insight AI. Menggunakan analisis fallback."
            ),
            contribution_margin_per_km=ContributionMargin(
                margin_rp=analysis_data['margin_analysis']['per_km'],
                category=analysis_data['margin_analysis']['category'],
                short_sentence=analysis_data['margin_analysis']['insight'],
                margin_insight="Error dalam menghasilkan insight AI. Menggunakan analisis fallback."
            ),
            overall_insight=OverallInsight(
                summary=f"Error dalam menghasilkan insight AI: {str(e)}. Menggunakan analisis fallback."
            )
        )

# Initialize the vehicle ROI analyzer
analyzer = VehicleROIAnalyzer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "language": "Indonesian",
        "output_format": "Structured JSON",
        "endpoints": {
            "/health": "Health check endpoint",
            "/analyze": "Vehicle ROI analysis endpoint"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_vehicle_roi():
    """
    Main API endpoint untuk analisis ROI kendaraan dengan output terstruktur untuk frontend.
    
    Expects JSON data dengan metrics kendaraan sesuai dengan VehicleInputData schema.
    
    Returns:
        JSON response dengan format terstruktur sesuai VehicleROIOutput untuk frontend
    """
    try:
        # Get JSON data from the HTTP request
        request_data = request.json
        
        # Validate that data was provided
        if not request_data:
            return jsonify({"error": "Tidak ada data yang diberikan"}), 400
        
        # Validate and deserialize input data using dataclass validation
        try:
            validated_data = validate_vehicle_data(request_data)
        except ValueError as err:
            return jsonify({"error": "Validasi data gagal", "details": str(err)}), 400
        
        # Process the validated data through Python analysis functions
        structured_analysis = analyzer.process_vehicle_data(validated_data)
        
        # Generate AI-powered structured analysis for frontend
        frontend_analysis = generate_structured_analysis(structured_analysis, validated_data)
        
        # Convert dataclass to dictionary for JSON serialization
        response_data = asdict(frontend_analysis)
        
        # Return the structured format that matches frontend requirements
        return jsonify(response_data)
    
    except Exception as e:
        # Return error response if anything fails
        return jsonify({"error": f"Analisis gagal: {str(e)}"}), 500

# Main execution block - only runs when script is executed directly (not imported)
if __name__ == '__main__':
    # Check if required environment variable is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key in the .env file")
        exit(1)
    
    # Run Flask development server
    app.run(host='0.0.0.0', port=8501)