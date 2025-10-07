import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any
import time

# Page configuration
st.set_page_config(
    page_title="Vehicle ROI Analyzer",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-card {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .danger-card {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .section-header {
        background: #f8fafc;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        margin: 1rem 0 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
FLASK_API_URL = "http://localhost:8501"

class StreamlitVehicleROIApp:
    def __init__(self):
        self.api_url = FLASK_API_URL
    
    def check_api_health(self):
        """Check if Flask API is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def call_analysis_api(self, data: Dict[str, Any]):
        """Call Flask API for analysis"""
        try:
            response = requests.post(
                f"{self.api_url}/analyze",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json()
        except Exception as e:
            return False, {"error": f"Connection error: {str(e)}"}
    
    def format_currency(self, value):
        """Format currency in Indonesian format"""
        try:
            return f"Rp {value:,.0f}".replace(',', '.')
        except:
            return f"Rp {value}"
    
    def get_category_color(self, category: str):
        """Get color based on category"""
        color_map = {
            "Sangat Layak": "#10b981",
            "Layak": "#059669", 
            "Perlu Dievaluasi": "#f59e0b",
            "Tidak Disarankan": "#ef4444",
            "Rugi": "#dc2626",
            "Sangat Efisien": "#10b981",
            "Efisien": "#059669",
            "Kurang Efisien": "#f59e0b", 
            "Tidak Efisien": "#ef4444",
            "Sangat Cepat": "#10b981",
            "Cepat": "#059669",
            "Lambat": "#f59e0b",
            "Sangat Lambat": "#ef4444",
            "Sangat Tinggi": "#10b981",
            "Tinggi": "#059669", 
            "Cukup": "#f59e0b",
            "Rendah": "#ef4444"
        }
        return color_map.get(category, "#6b7280")
    
    def create_roi_chart(self, roi_percentage: str, category: str):
        """Create ROI gauge chart"""
        # Extract numeric value from percentage string
        roi_value = float(roi_percentage.replace('%', ''))
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = roi_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "ROI %"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 250]},
                'bar': {'color': self.get_category_color(category)},
                'steps': [
                    {'range': [0, 70], 'color': "#fee2e2"},
                    {'range': [70, 100], 'color': "#fef3c7"},
                    {'range': [100, 150], 'color': "#d1fae5"},
                    {'range': [150, 250], 'color': "#dcfce7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    def create_cost_structure_pie(self, owning_pct: int, operational_pct: int):
        """Create cost structure pie chart"""
        fig = go.Figure(data=[go.Pie(
            labels=['Owning Cost', 'Operational Cost'],
            values=[owning_pct, operational_pct],
            hole=.3,
            marker_colors=['#3b82f6', '#10b981']
        )])
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_text="Cost Structure Distribution",
            height=300,
            showlegend=True
        )
        return fig
    
    def create_monthly_simulation_chart(self, monthly_data):
        """Create monthly simulation chart"""
        # Extract numeric values from formatted strings
        installment = float(monthly_data.get('installment', '0').replace('Rp ', '').replace('.', '').replace(',', ''))
        revenue = float(monthly_data.get('revenue', '0').replace('Rp ', '').replace('.', '').replace(',', ''))
        net_cashflow = revenue - installment
        
        categories = ['Installment', 'Revenue', 'Net Cashflow']
        values = [installment, revenue, net_cashflow]
        colors = ['#ef4444', '#10b981', '#3b82f6' if net_cashflow >= 0 else '#ef4444']
        
        fig = go.Figure(data=[
            go.Bar(x=categories, y=values, marker_color=colors, text=values, texttemplate='%{text:,.0f}')
        ])
        
        fig.update_layout(
            title="Monthly Cash Flow Simulation",
            yaxis_title="Amount (Rp)",
            height=300,
            showlegend=False
        )
        return fig
    
    def render_input_form(self):
        """Render the input form"""
        st.markdown('<div class="section-header"><h3>📊 Input Data Kendaraan</h3></div>', unsafe_allow_html=True)
        
        with st.form("vehicle_data_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Informasi Dasar")
                unit_name = st.text_input("Nama Unit Kendaraan*", value="Truck Fuso Fighter")
                segment = st.selectbox("Segmen Kendaraan*", 
                    ["Light Commercial Vehicle", "Medium Commercial Vehicle", "Heavy Commercial Vehicle", "Special Purpose Vehicle"])
                unit_price = st.number_input("Harga Unit (Rp)*", min_value=0.0, value=850000000.0, step=1000000.0)
                uses_leasing = st.checkbox("Menggunakan Skema Leasing")
                
                st.subheader("Biaya dan TCO")
                tco = st.number_input("Total Cost of Ownership (Rp)*", min_value=0.0, value=1200000000.0, step=1000000.0)
                annual_tco = st.number_input("TCO Tahunan (Rp)*", min_value=0.0, value=240000000.0, step=1000000.0)
                cost_per_km = st.number_input("Biaya per KM (Rp)*", min_value=0.0, value=5000.0, step=100.0)
            
            with col2:
                st.subheader("Revenue dan Profitabilitas")
                revenue_per_km = st.number_input("Revenue per KM (Rp)*", min_value=0.0, value=7500.0, step=100.0)
                contribution_margin = st.number_input("Contribution Margin per KM (Rp)*", min_value=0.0, value=2500.0, step=100.0)
                total_revenue = st.number_input("Total Revenue (Rp)*", min_value=0.0, value=1800000000.0, step=1000000.0)
                
                st.subheader("Metrics Kinerja")
                roi = st.number_input("ROI (decimal, contoh: 1.5 untuk 150%)*", min_value=0.0, value=1.25, step=0.05)
                bep_years = st.number_input("Break Even Point (Tahun)*", min_value=0.0, value=2.8, step=0.1)
                bep_km = st.number_input("Break Even Point (KM)*", min_value=0.0, value=336000.0, step=1000.0)
                
                st.subheader("Struktur Biaya (%)")
                col_owning, col_operational = st.columns(2)
                with col_owning:
                    owning_pct = st.slider("Owning Cost %", 0.0, 1.0, 0.55, 0.05)
                with col_operational:
                    operational_pct = st.slider("Operational Cost %", 0.0, 1.0, 0.45, 0.05)
                
                residual_value_pct = st.slider("Residual Value %", 0.0, 1.0, 0.30, 0.05)
            
            submitted = st.form_submit_button("🔍 Analisis ROI", use_container_width=True)
            
            if submitted:
                # Validate required fields
                required_fields = {
                    "unit_name": unit_name,
                    "segment": segment,
                    "unit_price": unit_price,
                    "tco": tco,
                    "annual_tco": annual_tco,
                    "cost_per_km": cost_per_km,
                    "revenue_per_km": revenue_per_km,
                    "contribution_margin": contribution_margin,
                    "total_revenue": total_revenue,
                    "roi": roi,
                    "bep_years": bep_years,
                    "bep_km": bep_km
                }
                
                missing_fields = [field for field, value in required_fields.items() if not value]
                
                if missing_fields:
                    st.error(f"Field wajib yang belum diisi: {', '.join(missing_fields)}")
                    return None
                
                # Prepare data for API
                api_data = {
                    "unit_name": unit_name,
                    "segment": segment,
                    "unit_price": unit_price,
                    "uses_leasing": uses_leasing,
                    "tco": tco,
                    "annual_tco": annual_tco,
                    "cost_per_km": cost_per_km,
                    "revenue_per_km": revenue_per_km,
                    "contribution_margin": contribution_margin,
                    "total_revenue": total_revenue,
                    "roi": roi,
                    "bep_years": bep_years,
                    "bep_km": bep_km,
                    "owning_pct": owning_pct,
                    "operational_pct": operational_pct,
                    "residual_value_pct": residual_value_pct
                }
                
                return api_data
        
        return None
    
    def render_analysis_results(self, results: Dict[str, Any]):
        """Render analysis results"""
        st.markdown('<div class="section-header"><h3>📈 Hasil Analisis ROI</h3></div>', unsafe_allow_html=True)
        
        # ROI Analysis Section
        st.markdown("### 🎯 Return on Investment (ROI)")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            roi_data = results["roi"]
            fig_roi = self.create_roi_chart(roi_data["percentage"], roi_data["category"])
            st.plotly_chart(fig_roi, use_container_width=True)
        
        with col2:
            category_color = self.get_category_color(roi_data["category"])
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: {category_color};">{roi_data["category"]}</h4>
                <p><strong>ROI:</strong> {roi_data["percentage"]}</p>
                <p><strong>Quick Insight:</strong> {roi_data["short_sentence"]}</p>
                <p><strong>Analysis:</strong> {roi_data["insight_narrative"]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # TCO Analysis Section
        st.markdown("### 💰 Total Cost of Ownership (TCO)")
        tco_data = results["tco"]
        category_color = self.get_category_color(tco_data["category"])
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {category_color};">Efisiensi Biaya: {tco_data["category"]}</h4>
            <p><strong>Biaya per KM:</strong> {tco_data["amount_rp"]}</p>
            <p><strong>Quick Insight:</strong> {tco_data["short_sentence"]}</p>
            <p><strong>Analysis:</strong> {tco_data["insight_narrative"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cost Structure Analysis
        st.markdown("### ⚖️ Struktur Biaya: Owning vs Operational")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            owning_data = results["owning_vs_operational"]
            fig_pie = self.create_cost_structure_pie(
                owning_data["owning_percentage"],
                owning_data["operational_percentage"]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            category_color = self.get_category_color(owning_data["category"])
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: {category_color};">Struktur: {owning_data["category"]}</h4>
                <p><strong>Owning Cost:</strong> {owning_data["owning_percentage"]}%</p>
                <p><strong>Operational Cost:</strong> {owning_data["operational_percentage"]}%</p>
                <p><strong>Quick Insight:</strong> {owning_data["short_sentence"]}</p>
                <p><strong>Cashflow Implication:</strong> {owning_data["cashflow_implication"]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Break Even Point Analysis
        st.markdown("### ⏱️ Break Even Point")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            bep_data = results["break_even_point"]
            # Create monthly simulation chart if data is available
            try:
                fig_monthly = self.create_monthly_simulation_chart(bep_data["monthly_simulation"])
                st.plotly_chart(fig_monthly, use_container_width=True)
            except:
                st.info("Monthly simulation data tidak tersedia untuk visualisasi")
        
        with col2:
            category_color = self.get_category_color(bep_data["category"])
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: {category_color};">Kecepatan BEP: {bep_data["category"]}</h4>
                <p><strong>Waktu BEP:</strong> {bep_data["period"]}</p>
                <p><strong>Jarak BEP:</strong> {bep_data["bep_km"]}</p>
                <p><strong>Quick Insight:</strong> {bep_data["short_sentence"]}</p>
                <p><strong>BEP Analysis:</strong> {bep_data["bep_insight"]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Monthly simulation details
            monthly_sim = bep_data["monthly_simulation"]
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 1rem;">
                <h5>Simulasi Bulanan</h5>
                <p><strong>Installment:</strong> {monthly_sim["installment"]}</p>
                <p><strong>Revenue:</strong> {monthly_sim["revenue"]}</p>
                <p><strong>Net Cashflow:</strong> {monthly_sim["net_cashflow"]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Contribution Margin Analysis
        st.markdown("### 📊 Contribution Margin per KM")
        margin_data = results["contribution_margin_per_km"]
        category_color = self.get_category_color(margin_data["category"])
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {category_color};">Margin Level: {margin_data["category"]}</h4>
            <p><strong>Margin per KM:</strong> {margin_data["margin_rp"]}</p>
            <p><strong>Quick Insight:</strong> {margin_data["short_sentence"]}</p>
            <p><strong>Margin Analysis:</strong> {margin_data["margin_insight"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Overall Insight
        st.markdown("### 🎯 Overall Business Insight")
        overall_insight = results["overall_insight"]["summary"]
        st.markdown(f"""
        <div class="success-card">
            <h4>📋 Executive Summary & Recommendations</h4>
            <p>{overall_insight}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main application runner"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🚛 Vehicle ROI Analyzer</h1>
            <p>Analisis Return on Investment untuk Kendaraan Transportasi Logistik</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Check API health
        if not self.check_api_health():
            st.error("⚠️ Flask API tidak dapat diakses. Pastikan server Flask berjalan di http://localhost:8501")
            st.info("Untuk menjalankan server Flask: `python app.py`")
            return
        
        st.success("✅ Terhubung dengan Flask API")
        
        # Input form
        form_data = self.render_input_form()
        
        # Process analysis if form is submitted
        if form_data:
            with st.spinner("🔄 Sedang menganalisis data..."):
                success, response = self.call_analysis_api(form_data)
            
            if success:
                st.success("✅ Analisis berhasil dilakukan!")
                self.render_analysis_results(response)
            else:
                st.error(f"❌ Analisis gagal: {response.get('error', 'Unknown error')}")
                if 'details' in response:
                    st.error(f"Details: {response['details']}")

# Initialize and run the app
if __name__ == "__main__":
    app = StreamlitVehicleROIApp()
    app.run()