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
    summary: str = ""
    key_insight: str = ""

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
    """Generate structured analysis for frontend using Gemini with safe, neutral prompts.
       Guarantees structured output even if model is blocked (deterministic fallback)."""
    

    # ---------- Helpers ----------

    def pick_bep_non_leasing_sentence(period: str, category: str, seed: str = "") -> str:
        variants = [
            f"Periode {period} dikategorikan {category}. Simulasi bulanan tidak diterapkan karena tanpa leasing.",
            f"BEP {period} termasuk {category}. Tidak ada simulasi cicilan bulanan (tanpa leasing).",
            f"Estimasi balik modal {period}—kategori {category}. Simulasi bulanan tidak relevan (tanpa leasing).",
            f"Balik modal diperkirakan {period} ({category}). Tidak ada komponen cicilan bulanan.",
            f"Horizon BEP {period} diklasifikasikan {category}. Perhitungan arus kas bulanan tidak digunakan karena tidak ada leasing.",
            f"Durasi BEP {period}—{category}. Simulasi cicilan bulanan tidak berlaku.",
            f"Waktu impas {period} ({category}). Bagian simulasi bulanan diabaikan (tanpa leasing).",
            f"Perkiraan BEP {period} pada kategori {category}. Tidak terdapat cicilan bulanan.",
            f"BEP {period}: {category}. Modul simulasi bulanan tidak aktif (tanpa leasing).",
            f"BEP {period} tergolong {category}. Simulasi bulanan tidak disertakan (non-leasing).",
        ]
        idx = (abs(hash(seed)) % len(variants)) if seed else 0
        return variants[idx]


    def sanitize_neutral(text: str) -> str:
        """Potong kalimat begitu terdeteksi kata yang berpotensi memicu safety/aksi."""
        if not text:
            return ""
        banned = [
            "namun", "di sisi lain", "rekomendasi", "strategi", "harus",
            "segera", "prioritas", "tantangan", "disarankan", "anjurkan",
            "sebaiknya", "langkah", "action", "mitigasi", "optimasi"
        ]
        t = text.strip()
        low = t.lower()
        cut = min([low.find(w) for w in banned if low.find(w) != -1] or [len(t)])
        t = t[:cut].rstrip(" .,\n")
        return (t + ".") if t and not t.endswith(".") else t

    def build_neutral_output(analysis: Dict[str, Any], vd: VehicleInputData) -> VehicleROIOutput:
        """Deterministic, objective narratives from computed numbers (no model)."""
        roi_pct = analysis["roi_analysis"]["value"]
        roi_cat = analysis["roi_analysis"]["category"]
        roi_short = f"ROI tercatat {roi_pct} dengan kategori {roi_cat}."
        roi_long = f"Nilai ROI {roi_pct} merefleksikan kinerja pengembalian sesuai kategori {roi_cat} berdasarkan indikator internal."

        per_km = analysis["tco_analysis"]["per_km"]
        eff = analysis["tco_analysis"]["efficiency"]
        tco_short = f"Biaya operasional per kilometer {per_km} dengan klasifikasi {eff}."
        tco_long = f"Biaya per kilometer {per_km} menunjukkan tingkat efisiensi operasional pada kategori {eff} menurut parameter yang digunakan."

        own = analysis["cost_structure"]["owning_percentage"]
        opx = analysis["cost_structure"]["operational_percentage"]
        struct_type = analysis["cost_structure"]["structure_type"]
        struct_short = f"Komposisi biaya: Owning {own}, Operational {opx} ({struct_type})."
        struct_imp = f"Komposisi tersebut mencerminkan struktur biaya pada kategori {struct_type} sesuai pembobotan persentase."

        bep_period = analysis["bep_analysis"]["years_formatted"]
        bep_km = analysis["bep_analysis"]["kilometers"]
        bep_cat = analysis["bep_analysis"]["category"]
        bep_short = f"Perkiraan BEP {bep_period} dengan jarak {bep_km}."
        if vd.uses_leasing:
            _mi = vd.annual_tco / 12
            _mr = (vd.total_revenue / (vd.bep_years * 12)) if vd.bep_years > 0 else 0
            _mn = _mr - _mi
            monthly_installment = f"Rp {_mi:,.0f}".replace(',', '.')
            monthly_revenue = f"Rp {_mr:,.0f}".replace(',', '.')
            monthly_net = f"Rp {_mn:,.0f}".replace(',', '.')
            bep_ins = (
                f"Periode {bep_period} dikategorikan {bep_cat}. "
                f"Simulasi bulanan: cicilan {monthly_installment}, pendapatan {monthly_revenue}, net cashflow {monthly_net}."
            )
        else:
            _mr = (vd.total_revenue / (vd.bep_years * 12)) if vd.bep_years > 0 else 0
            monthly_installment = "Tidak ada cicilan"
            monthly_revenue = f"Rp {_mr:,.0f}".replace(',', '.')
            monthly_net = monthly_revenue  # sama, tanpa cicilan
            bep_ins = (
                f"Periode {bep_period} dikategorikan {bep_cat}. "
                f"Simulasi bulanan: tidak berlaku (tanpa leasing)."
            )
        
        # --- Compose string untuk MonthlySimulation (pakai nama yang benar) ---
        if vd.uses_leasing:
            ms_installment = f"{monthly_installment} per bulan"
            ms_revenue = f"{monthly_revenue} per bulan"
            ms_net = f"{monthly_net} per bulan"
        else:
            ms_installment = "Tidak berlaku (tanpa leasing)"
            ms_revenue = "Tidak berlaku (tanpa leasing)"
            ms_net = "Tidak berlaku (tanpa leasing)"

        margin_rp = analysis["margin_analysis"]["per_km"]
        margin_cat = analysis["margin_analysis"]["category"]
        margin_short = f"Margin kontribusi per km {margin_rp} (kategori {margin_cat})."
        margin_long = f"Nilai margin {margin_rp} menggambarkan kontribusi per kilometer sesuai kategori {margin_cat} berdasarkan perhitungan internal."

        oi_summary = (
            f"Analisis menunjukkan ROI {roi_pct}, biaya per kilometer {per_km}, "
            f"komposisi biaya Owning {own} dan Operational {opx}, serta perkiraan BEP {bep_period}. "
            f"Informasi tersebut menggambarkan kondisi finansial unit berdasarkan parameter yang digunakan."
        )
        key = f"Kondisi umum selaras dengan kategori ROI: {roi_cat}."

        return VehicleROIOutput(
            roi=ROIAnalysis(
                percentage=roi_pct,
                category=roi_cat,
                short_sentence=sanitize_neutral(roi_short),
                insight_narrative=sanitize_neutral(roi_long),
            ),
            tco=TCOAnalysis(
                amount_rp=per_km,
                category=eff,
                short_sentence=sanitize_neutral(tco_short),
                insight_narrative=sanitize_neutral(tco_long),
            ),
            owning_vs_operational=OwningVsOperational(
                owning_percentage=int(vd.owning_pct * 100),
                operational_percentage=int(vd.operational_pct * 100),
                category=struct_type,
                short_sentence=sanitize_neutral(struct_short),
                cashflow_implication=sanitize_neutral(struct_imp),
                pie_chart_data=PieChartData(
                    owning_cost=int(vd.owning_pct * 100),
                    operational_cost=int(vd.operational_pct * 100),
                ),
            ),
            break_even_point=BreakEvenPoint(
                period=bep_period,
                bep_km=bep_km,
                category=bep_cat,
                short_sentence=sanitize_neutral(bep_short),
                monthly_simulation=MonthlySimulation(
                    installment=ms_installment,
                    revenue=ms_revenue,
                    net_cashflow=ms_net,
                ),
                bep_insight=sanitize_neutral(bep_ins),
            ),
            contribution_margin_per_km=ContributionMargin(
                margin_rp=margin_rp,
                category=margin_cat,
                short_sentence=sanitize_neutral(margin_short),
                margin_insight=sanitize_neutral(margin_long),
            ),
            overall_insight=OverallInsight(
                summary=sanitize_neutral(oi_summary),
                key_insight=sanitize_neutral(key),
            ),
            
        )

    # ---------- Build prompt (tanpa warnings_text) ----------
    # Hitung simulasi bulanan -> hanya ada cicilan jika uses_leasing = True
    if raw_data.uses_leasing:
        monthly_installment = raw_data.annual_tco / 12
        monthly_revenue = raw_data.total_revenue / (raw_data.bep_years * 12) if raw_data.bep_years > 0 else 0
        monthly_net_cashflow = monthly_revenue - monthly_installment
        monthly_line_for_prompt = f"- Simulasi Bulanan: cicilan Rp {monthly_installment:,.0f}, pendapatan Rp {monthly_revenue:,.0f}, net cashflow Rp {monthly_net_cashflow:,.0f}"
        monthly_installment_str = f"Rp {monthly_installment:,.0f} per bulan"
        monthly_revenue_str = f"Rp {monthly_revenue:,.0f} per bulan"
        monthly_netcash_str = f"Rp {monthly_net_cashflow:,.0f} per bulan"
    else:
        monthly_installment = 0.0
        monthly_revenue = raw_data.total_revenue / (raw_data.bep_years * 12) if raw_data.bep_years > 0 else 0
        monthly_net_cashflow = monthly_revenue  # tak ada cicilan -> net = revenue
        monthly_line_for_prompt = "- Simulasi Bulanan: tidak berlaku (tanpa leasing)"
        monthly_installment_str = "Tidak ada cicilan"
        monthly_revenue_str = f"Rp {monthly_revenue:,.0f} per bulan"
        monthly_netcash_str = f"Rp {monthly_net_cashflow:,.0f} per bulan"


    prompt = f"""PERAN: Anda adalah sistem peringkas data yang menghasilkan deskripsi objektif (bukan saran).

TUJUAN: Hasilkan ringkasan netral, singkat, dan jelas (tanpa rekomendasi/daftar).

DATA KENDARAAN:
- Nama: {analysis_data['unit_info']['name']}
- Segmen: {analysis_data['unit_info']['segment']}
- Harga Unit: {analysis_data['unit_info']['price']}
- Menggunakan Leasing: {"Ya" if raw_data.uses_leasing else "Tidak"}
- Residual Value: {int(raw_data.residual_value_pct * 100)}%

METRIK:
- ROI: {analysis_data['roi_analysis']['value']} [{analysis_data['roi_analysis']['category']}]
- TCO/km: {analysis_data['tco_analysis']['per_km']} [{analysis_data['tco_analysis']['efficiency']}]
- Struktur Biaya: Owning {analysis_data['cost_structure']['owning_percentage']}, Operational {analysis_data['cost_structure']['operational_percentage']} [{analysis_data['cost_structure']['structure_type']}]
- BEP: {analysis_data['bep_analysis']['years_formatted']} [{analysis_data['bep_analysis']['category']}], {analysis_data['bep_analysis']['kilometers']}
- Margin/km: {analysis_data['margin_analysis']['per_km']} [{analysis_data['margin_analysis']['category']}]
- {monthly_line_for_prompt}

INSTRUKSI OUTPUT (WAJIB):
- Keluaran hanya JSON, tanpa teks lain, tanpa daftar/bullet, tanpa saran/ajakan bertindak.
- Nada netral dan deskriptif.
- Format PASTI:

{{
  "roi": {{
    "percentage": "{analysis_data['roi_analysis']['value']}",
    "category": "{analysis_data['roi_analysis']['category']}",
    "short_sentence": "…",
    "insight_narrative": "…"
  }},
  "tco": {{
    "amount_rp": "{analysis_data['tco_analysis']['per_km']}",
    "category": "{analysis_data['tco_analysis']['efficiency']}",
    "short_sentence": "…",
    "insight_narrative": "…"
  }},
  "owning_vs_operational": {{
    "owning_percentage": {int(raw_data.owning_pct * 100)},
    "operational_percentage": {int(raw_data.operational_pct * 100)},
    "category": "{analysis_data['cost_structure']['structure_type']}",
    "short_sentence": "…",
    "cashflow_implication": "…",
    "pie_chart_data": {{
      "owning_cost": {int(raw_data.owning_pct * 100)},
      "operational_cost": {int(raw_data.operational_pct * 100)}
    }}
  }},
  "break_even_point": {{
    "period": "{analysis_data['bep_analysis']['years_formatted']}",
    "bep_km": "{analysis_data['bep_analysis']['kilometers']}",
    "category": "{analysis_data['bep_analysis']['category']}",
    "short_sentence": "…",
    "monthly_simulation": {{
      "installment": "{monthly_installment_str}",
      "revenue": "{monthly_revenue_str}",
      "net_cashflow": "{monthly_netcash_str}"

    }},
    "bep_insight": "…"
  }},
  "contribution_margin_per_km": {{
    "margin_rp": "{analysis_data['margin_analysis']['per_km']}",
    "category": "{analysis_data['margin_analysis']['category']}",
    "short_sentence": "…",
    "margin_insight": "…"
  }},
  "overall_insight": {{
    "summary": "Paragraf ringkas (≤4 kalimat) bersifat deskriptif dan netral.",
    "key_insight": "1 kalimat simpulan faktual (mis. selaras dengan kategori ROI)."
  }}
}}"""

    # ---------- Call Gemini safely ----------
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=(
                "Anda menghasilkan deskripsi objektif. "
                "Dilarang memberi saran, rekomendasi, atau ajakan bertindak. "
                "Seluruh keluaran harus netral dan informatif."
            ),
        )

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1200,
                temperature=0.3,
                response_mime_type="application/json",
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        )

        if not response.candidates or not response.candidates[0].content.parts:
            return build_neutral_output(analysis_data, raw_data)

        raw_text = response.text.strip()
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            if "```json" in raw_text:
                s = raw_text.find("```json") + 7
                e = raw_text.find("```", s)
                json_text = raw_text[s:e].strip()
                data = json.loads(json_text)
            else:
                return build_neutral_output(analysis_data, raw_data)

        # Sanitasi output agar netral
        if "overall_insight" in data:
            data["overall_insight"]["summary"] = sanitize_neutral(data["overall_insight"].get("summary", ""))
            data["overall_insight"]["key_insight"] = sanitize_neutral(data["overall_insight"].get("key_insight", ""))

        # --- POST-PROCESS: paksa logika leasing/non-leasing ---
        bep = data.get("break_even_point", {})
        ms = bep.get("monthly_simulation", {})

        if not raw_data.uses_leasing:
            # Non-leasing → nolkan/disable simulasi bulanan
            ms["installment"] = "Tidak berlaku (tanpa leasing)"
            ms["revenue"] = "Tidak berlaku (tanpa leasing)"
            ms["net_cashflow"] = "Tidak berlaku (tanpa leasing)"
            bep["monthly_simulation"] = ms

            # Ganti narasi BEP agar tidak menyebut cicilan
            period = bep.get("period", analysis_data["bep_analysis"]["years_formatted"])
            category = bep.get("category", analysis_data["bep_analysis"]["category"])
            bep["bep_insight"] = sanitize_neutral(
                pick_bep_non_leasing_sentence(period, category, seed=analysis_data["unit_info"]["name"])
            )

        else:
            # Leasing aktif → pastikan angka simulasi sesuai perhitungan backend
            monthly_installment = f"Rp {raw_data.annual_tco/12:,.0f}".replace(',', '.')
            monthly_revenue = f"Rp {(raw_data.total_revenue/(raw_data.bep_years*12) if raw_data.bep_years > 0 else 0):,.0f}".replace(',', '.')
            monthly_net = f"Rp {(raw_data.total_revenue/(raw_data.bep_years*12) - raw_data.annual_tco/12 if raw_data.bep_years > 0 else -raw_data.annual_tco/12):,.0f}".replace(',', '.')

            ms["installment"] = f"{monthly_installment} per bulan"
            ms["revenue"] = f"{monthly_revenue} per bulan"
            ms["net_cashflow"] = f"{monthly_net} per bulan"
            bep["monthly_simulation"] = ms

        # Tulis kembali ke data
        data["break_even_point"] = bep



        if "owning_vs_operational" in data and "pie_chart_data" not in data["owning_vs_operational"]:
            data["owning_vs_operational"]["pie_chart_data"] = {
                "owning_cost": data["owning_vs_operational"]["owning_percentage"],
                "operational_cost": data["owning_vs_operational"]["operational_percentage"],
            }

        return VehicleROIOutput(
            roi=ROIAnalysis(**data["roi"]),
            tco=TCOAnalysis(**data["tco"]),
            owning_vs_operational=OwningVsOperational(
                owning_percentage=data["owning_vs_operational"]["owning_percentage"],
                operational_percentage=data["owning_vs_operational"]["operational_percentage"],
                category=data["owning_vs_operational"]["category"],
                short_sentence=sanitize_neutral(data["owning_vs_operational"]["short_sentence"]),
                cashflow_implication=sanitize_neutral(data["owning_vs_operational"]["cashflow_implication"]),
                pie_chart_data=PieChartData(**data["owning_vs_operational"]["pie_chart_data"]),
            ),
            break_even_point=BreakEvenPoint(
                period=data["break_even_point"]["period"],
                bep_km=data["break_even_point"]["bep_km"],
                category=data["break_even_point"]["category"],
                short_sentence=sanitize_neutral(data["break_even_point"]["short_sentence"]),
                monthly_simulation=MonthlySimulation(**data["break_even_point"]["monthly_simulation"]),
                bep_insight=sanitize_neutral(data["break_even_point"]["bep_insight"]),
            ),
            contribution_margin_per_km=ContributionMargin(
                **{
                    "margin_rp": data["contribution_margin_per_km"]["margin_rp"],
                    "category": data["contribution_margin_per_km"]["category"],
                    "short_sentence": sanitize_neutral(data["contribution_margin_per_km"]["short_sentence"]),
                    "margin_insight": sanitize_neutral(data["contribution_margin_per_km"]["margin_insight"]),
                }
            ),
            overall_insight=OverallInsight(
                summary=data["overall_insight"]["summary"],
                key_insight=data["overall_insight"]["key_insight"],
            ),
        )

    except Exception:
        return build_neutral_output(analysis_data, raw_data)

    
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
                summary=f"Error dalam menghasilkan insight AI: {str(e)}. Menggunakan analisis fallback.",
                key_insight=""
            )
        )

    # ==============================================================
    #  BUSINESS NARRATIVE GENERATOR (untuk output seperti contoh kamu)
    # ==============================================================
def generate_business_narrative(analysis_data: Dict[str, Any], vd: VehicleInputData) -> Dict[str, str]:
    """Generate formatted business insight narrative for presentation or frontend display."""
    
    # ROI
    roi_val = analysis_data["roi_analysis"]["value"]
    roi_cat = analysis_data["roi_analysis"]["category"]
    roi_msg = analysis_data["roi_analysis"]["insight"]
    roi_text = (
        f"### ROI\n\n**{roi_val} – {roi_cat}**\n"
        f"{roi_msg}.\n"
        f"ROI ini menunjukkan bahwa **{vd.unit_name}** di segmen *{vd.segment}* memiliki potensi pengembalian modal yang solid. "
        f"Dengan strategi operasional yang konsisten dan efisiensi biaya, profit dapat terus dipertahankan bahkan di pasar yang fluktuatif."
    )

    # TCO
    tco_total = analysis_data["tco_analysis"]["total"]
    tco_cat = analysis_data["tco_analysis"]["efficiency"]
    tco_msg = analysis_data["tco_analysis"]["insight"]
    tco_per_km = analysis_data["tco_analysis"]["per_km"]
    tco_text = (
        f"### TCO\n\n**{tco_total} – {tco_cat}**\n"
        f"{tco_msg}.\n"
        f"Dengan **biaya per km {tco_per_km}**, operasional {vd.unit_name} berada dalam kisaran efisien, "
        f"memberikan ruang margin yang sehat dan menekan risiko tekanan biaya di masa mendatang."
    )

    # Cost Structure
    own = analysis_data["cost_structure"]["owning_percentage"]
    opx = analysis_data["cost_structure"]["operational_percentage"]
    struct_cat = analysis_data["cost_structure"]["structure_type"]
    struct_msg = analysis_data["cost_structure"]["insight"]
    cost_structure_text = (
        f"### Owning vs Operational Cost\n\n**Owning {own}** | **Operational {opx}** – {struct_cat}\n"
        f"{struct_msg}.\n"
        f"Porsi kepemilikan dan biaya operasional yang seimbang mengindikasikan distribusi CAPEX dan OPEX yang terkontrol, "
        f"mendukung stabilitas arus kas tanpa ketergantungan berlebihan pada salah satu sisi."
    )

    # BEP
    bep_period = analysis_data["bep_analysis"]["years_formatted"]
    bep_km = analysis_data["bep_analysis"]["kilometers"]
    bep_cat = analysis_data["bep_analysis"]["category"]
    bep_msg = analysis_data["bep_analysis"]["insight"]
    if vd.uses_leasing:
        monthly_install = f"Rp {vd.annual_tco/12:,.0f}".replace(',', '.')
        monthly_rev = f"Rp {vd.total_revenue/(vd.bep_years*12):,.0f}".replace(',', '.')
        monthly_net = f"Rp {(vd.total_revenue/(vd.bep_years*12) - vd.annual_tco/12):,.0f}".replace(',', '.')
        leasing_text = (
            f"Dengan asumsi leasing aktif, estimasi cicilan bulanan **{monthly_install}**, "
            f"pendapatan **{monthly_rev}**, dan net cashflow **{monthly_net}**."
        )
    else:
        monthly_rev = f"Rp {vd.total_revenue/(vd.bep_years*12):,.0f}".replace(',', '.')
        leasing_text = (
            f"Dengan asumsi tanpa leasing, estimasi pendapatan bulanan sekitar **{monthly_rev}**, "
            f"menunjukkan posisi aman untuk perencanaan jangka menengah."
        )
    bep_text = (
        f"### Break Even Point\n\n**{bep_period} | {bep_km} – {bep_cat}**\n"
        f"{bep_msg}.\n"
        f"{leasing_text}"
    )

    # Margin
    margin_val = analysis_data["margin_analysis"]["per_km"]
    margin_cat = analysis_data["margin_analysis"]["category"]
    margin_msg = analysis_data["margin_analysis"]["insight"]
    margin_text = (
        f"### Contribution Margin per KM\n\n**{margin_val} – {margin_cat}**\n"
        f"{margin_msg}.\n"
        f"Margin ini memberikan bantalan yang memadai untuk mengatasi kenaikan biaya bahan bakar atau perawatan, "
        f"serta cukup fleksibel untuk memberikan diskon taktis pada kondisi pasar tertentu."
    )

    # Overall
    overall_text = (
        f"### Overall Insight\n\n"
        f"**{vd.unit_name}** di segmen *{vd.segment}* menunjukkan profil investasi yang {roi_cat.lower()}, "
        f"dengan ROI {roi_val} dan BEP {bep_period} yang tergolong {bep_cat.lower()}. "
        f"TCO berada pada level {tco_cat.lower()}, struktur biaya {struct_cat.lower()}, "
        f"dan margin kontribusi per km yang {margin_cat.lower()}. "
        f"Kombinasi ini menciptakan fondasi kuat untuk menjaga profitabilitas dan fleksibilitas strategi harga.\n"
        f"**Key Insight:** Fokus pada peningkatan utilisasi dan volume muatan berpotensi mempercepat BEP dan mendorong ROI di atas 120%."
    )

    return {
        "ROI": roi_text,
        "TCO": tco_text,
        "CostStructure": cost_structure_text,
        "BreakEven": bep_text,
        "Margin": margin_text,
        "Overall": overall_text,
    }


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
    """
    try:
        request_data = request.json
        if not request_data:
            return jsonify({"error": "Tidak ada data yang diberikan"}), 400

        try:
            validated_data = validate_vehicle_data(request_data)
        except ValueError as err:
            return jsonify({"error": "Validasi data gagal", "details": str(err)}), 400

        structured_analysis = analyzer.process_vehicle_data(validated_data)
        frontend_analysis = generate_structured_analysis(structured_analysis, validated_data)
        business_narrative = generate_business_narrative(structured_analysis, validated_data)

        from dataclasses import is_dataclass
        if is_dataclass(frontend_analysis):
            response_data = asdict(frontend_analysis)
        else:
            response_data = frontend_analysis

        response_data["business_narrative"] = business_narrative
        return jsonify(response_data)

    except Exception as e:
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