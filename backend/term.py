#!/usr/bin/env python3
"""
Vehicle ROI Analysis Terminal Client - Indonesian Version
Terminal client untuk analisis ROI kendaraan transportasi logistik
Updated for new structured JSON API response format
"""

import json
import requests
from typing import Dict, Any, Optional
import sys
import re

# Try to import rich for better markdown rendering, fall back to basic if not available
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.prompt import FloatPrompt, IntPrompt, Prompt, Confirm
    from rich.json import JSON
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class VehicleROITerminal:
    """Terminal client untuk Vehicle ROI Analysis API dengan dukungan markdown."""
    
    def __init__(self, api_url: str = "http://localhost:8501"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def print_markdown(self, text: str):
        """Print markdown text dengan formatting yang tepat."""
        if RICH_AVAILABLE:
            md = Markdown(text)
            self.console.print(md)
        else:
            # Basic markdown parsing
            lines = text.split('\n')
            for line in lines:
                if line.startswith('# '):
                    print(f"\n{'='*60}")
                    print(f"  {line[2:].upper()}")
                    print('='*60)
                elif line.startswith('## '):
                    print(f"\n{line[3:]}")
                    print('-'*len(line[3:]))
                elif line.startswith('### '):
                    print(f"\n{line[4:]}")
                elif '**' in line:
                    line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                    print(line)
                elif line.strip().startswith('- '):
                    print(f"  • {line.strip()[2:]}")
                else:
                    print(line)
    
    def print_json(self, data: Dict[str, Any], title: str = ""):
        """Print JSON data dengan syntax highlighting jika tersedia."""
        if RICH_AVAILABLE:
            if title:
                self.console.print(f"\n[bold blue]{title}[/bold blue]")
            json_obj = JSON.from_data(data)
            self.console.print(json_obj)
        else:
            if title:
                print(f"\n{title}")
                print("-" * len(title))
            print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def show_menu(self, options: list) -> int:
        """Tampilkan menu bernomor dan dapatkan pilihan user."""
        if RICH_AVAILABLE:
            for i, option in enumerate(options, 1):
                self.console.print(f"[bold yellow]{i}[/bold yellow]. {option}")
            
            while True:
                try:
                    choice = IntPrompt.ask(
                        "\n[bold green]Pilih opsi[/bold green]",
                        choices=[str(i) for i in range(1, len(options) + 1)]
                    )
                    return choice
                except KeyboardInterrupt:
                    return -1
        else:
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = input("\nPilih opsi (nomor): ").strip()
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(options):
                        return choice_num
                    else:
                        print(f"Silakan masukkan nomor antara 1 dan {len(options)}")
                except (ValueError, KeyboardInterrupt):
                    return -1
    
    def print_banner(self):
        """Print welcome banner."""
        banner_text = """
# 🚛 Vehicle ROI Analysis Terminal

Analisis ROI kendaraan untuk transportasi logistik dengan AI
Powered by Google Gemini | Format Output: Structured JSON
        """
        self.print_markdown(banner_text)
    
    def clear_screen(self):
        """Clear terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def check_api_health(self) -> bool:
        """Cek apakah API berjalan dan sehat."""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                status_text = f"""
## ✅ Status API: {health_data.get('status', 'Unknown')}
**URL**: {self.api_url}
**Bahasa**: {health_data.get('language', 'Indonesian')}
**Versi**: {health_data.get('version', '2.0.0')}
**Output Format**: {health_data.get('output_format', 'Structured JSON')}

### Endpoints Tersedia:
                """
                self.print_markdown(status_text)
                
                if 'endpoints' in health_data:
                    for endpoint, description in health_data['endpoints'].items():
                        self.print_markdown(f"- **{endpoint}**: {description}")
                
                return True
            else:
                self.print_markdown(f"## ❌ Error API: Status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_markdown(f"## ❌ Koneksi Gagal: {str(e)}")
            return False
    
    def get_float_input(self, prompt: str, allow_skip: bool = True) -> Optional[float]:
        """Dapatkan input float dari user dengan validasi."""
        if RICH_AVAILABLE:
            try:
                skip_text = " [dim](Enter untuk skip)[/dim]" if allow_skip else ""
                value = FloatPrompt.ask(
                    f"[cyan]{prompt}[/cyan]{skip_text}",
                    default=None if allow_skip else 0.0
                )
                return value
            except KeyboardInterrupt:
                return 'quit'
        else:
            skip_text = " (Enter untuk skip)" if allow_skip else ""
            user_input = input(f"{prompt}{skip_text}: ").strip()
            if not user_input and allow_skip:
                return None
            try:
                return float(user_input) if user_input else 0.0
            except ValueError:
                print("Input tidak valid, masukkan angka.")
                return self.get_float_input(prompt, allow_skip)
    
    def get_int_input(self, prompt: str, allow_skip: bool = True) -> Optional[int]:
        """Dapatkan input integer dari user dengan validasi."""
        if RICH_AVAILABLE:
            try:
                skip_text = " [dim](Enter untuk skip)[/dim]" if allow_skip else ""
                value = IntPrompt.ask(
                    f"[cyan]{prompt}[/cyan]{skip_text}",
                    default=None if allow_skip else 0
                )
                return value
            except KeyboardInterrupt:
                return 'quit'
        else:
            skip_text = " (Enter untuk skip)" if allow_skip else ""
            user_input = input(f"{prompt}{skip_text}: ").strip()
            if not user_input and allow_skip:
                return None
            try:
                return int(user_input) if user_input else 0
            except ValueError:
                print("Input tidak valid, masukkan angka bulat.")
                return self.get_int_input(prompt, allow_skip)
    
    def get_string_input(self, prompt: str, allow_skip: bool = True) -> Optional[str]:
        """Dapatkan input string dari user."""
        if RICH_AVAILABLE:
            try:
                skip_text = " [dim](Enter untuk skip)[/dim]" if allow_skip else ""
                value = Prompt.ask(
                    f"[cyan]{prompt}[/cyan]{skip_text}",
                    default=None if allow_skip else ""
                )
                return value if value else None
            except KeyboardInterrupt:
                return 'quit'
        else:
            skip_text = " (Enter untuk skip)" if allow_skip else ""
            user_input = input(f"{prompt}{skip_text}: ").strip()
            return user_input if user_input else None
    
    def get_boolean_input(self, prompt: str) -> Optional[bool]:
        """Dapatkan input boolean dari user."""
        if RICH_AVAILABLE:
            try:
                return Confirm.ask(f"[cyan]{prompt}[/cyan]")
            except KeyboardInterrupt:
                return 'quit'
        else:
            while True:
                user_input = input(f"{prompt} (y/n): ").strip().lower()
                if user_input in ['y', 'yes', 'ya', 'true', '1']:
                    return True
                elif user_input in ['n', 'no', 'tidak', 'false', '0']:
                    return False
                elif user_input == '':
                    return None
                else:
                    print("Masukkan y/n, yes/no, atau ya/tidak")
    
    def collect_json_input(self) -> Optional[Dict[str, Any]]:
        """Kumpulkan data kendaraan dari input JSON lengkap."""
        self.print_markdown("## � MInput JSON Lengkap")
        self.print_markdown("*Paste JSON data kendaraan Anda di bawah ini*")
        
        sample_json = """{
    "unit_name": "Truk Hino 500",
    "segment": "Urban Logistics", 
    "unit_price": 800000000,
    "uses_leasing": false,
    "tco": 1200000000,
    "annual_tco": 240000000,
    "cost_per_km": 5000,
    "revenue_per_km": 7500,
    "contribution_margin": 2500,
    "total_revenue": 1500000000,
    "roi": 1.15,
    "bep_years": 2.5,
    "bep_km": 150000,
    "owning_pct": 0.65,
    "operational_pct": 0.35,
    "residual_value_pct": 0.30
}"""
        
        self.print_markdown("### Contoh format JSON:")
        if RICH_AVAILABLE:
            json_obj = JSON(sample_json)
            self.console.print(json_obj)
        else:
            print(sample_json)
        
        self.print_markdown("\n### Masukkan JSON Anda:")
        self.print_markdown("*Ketik atau paste JSON, lalu tekan Enter dua kali untuk selesai*")
        
        json_lines = []
        empty_line_count = 0
        
        while True:
            try:
                if RICH_AVAILABLE:
                    line = input()
                else:
                    line = input()
                
                if line.strip() == "":
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                    json_lines.append(line)
                    
            except KeyboardInterrupt:
                return None
        
        if not json_lines:
            self.print_markdown("### ❌ Tidak ada input JSON yang diberikan")
            return None
        
        json_text = '\n'.join(json_lines)
        
        try:
            data = json.loads(json_text)
            self.print_markdown("### ✅ JSON berhasil diparse!")
            self.print_json(data, "Data yang akan dianalisis")
            
            if RICH_AVAILABLE:
                confirm = Confirm.ask("[green]Lanjutkan dengan data ini?[/green]")
            else:
                confirm = input("Lanjutkan dengan data ini? (y/n): ").strip().lower() in ['y', 'yes', 'ya']
            
            return data if confirm else None
            
        except json.JSONDecodeError as e:
            self.print_markdown(f"### ❌ Error parsing JSON: {str(e)}")
            self.print_markdown("Silakan coba lagi dengan format JSON yang valid")
            return None

    def collect_vehicle_data(self) -> Optional[Dict[str, Any]]:
        """Kumpulkan data kendaraan dari input user."""
        self.print_markdown("## 📝 Masukkan Data Kendaraan")
        self.print_markdown("*Semua field opsional kecuali yang ditandai*")
        
        data = {}
        
        # Basic vehicle info
        self.print_markdown("### 🚛 Informasi Kendaraan")
        unit_name = self.get_string_input("Nama kendaraan/Unit Name", False)
        if unit_name == 'quit':
            return None
        data['unit_name'] = unit_name or "Kendaraan"
        
        segment = self.get_string_input("Segmen (mis. Urban Logistics, Mining)")
        if segment == 'quit':
            return None
        if segment:
            data['segment'] = segment
        
        unit_price = self.get_float_input("Harga kendaraan (Rp)")
        if unit_price == 'quit':
            return None
        if unit_price:
            data['unit_price'] = unit_price
        
        uses_leasing = self.get_boolean_input("Menggunakan leasing?")
        if uses_leasing == 'quit':
            return None
        if uses_leasing is not None:
            data['uses_leasing'] = uses_leasing
        
        # Financial metrics
        self.print_markdown("### 💰 Metrik Finansial")
        
        tco = self.get_float_input("Total Cost of Ownership/TCO (Rp)")
        if tco == 'quit':
            return None
        if tco:
            data['tco'] = tco
        
        annual_tco = self.get_float_input("Total biaya tahunan (Rp)")
        if annual_tco == 'quit':
            return None
        if annual_tco:
            data['annual_tco'] = annual_tco
        
        cost_per_km = self.get_float_input("Biaya per kilometer (Rp)")
        if cost_per_km == 'quit':
            return None
        if cost_per_km:
            data['cost_per_km'] = cost_per_km
        
        revenue_per_km = self.get_float_input("Pendapatan per kilometer (Rp)")
        if revenue_per_km == 'quit':
            return None
        if revenue_per_km:
            data['revenue_per_km'] = revenue_per_km
        
        contribution_margin = self.get_float_input("Margin kontribusi per KM (Rp)")
        if contribution_margin == 'quit':
            return None
        if contribution_margin:
            data['contribution_margin'] = contribution_margin
        
        total_revenue = self.get_float_input("Total pendapatan selama holding period (Rp)")
        if total_revenue == 'quit':
            return None
        if total_revenue:
            data['total_revenue'] = total_revenue
        
        # ROI and performance metrics
        self.print_markdown("### 📈 Metrik Performa")
        
        roi = self.get_float_input("ROI (rasio, contoh 1.06 untuk 106%)")
        if roi == 'quit':
            return None
        if roi:
            data['roi'] = roi
        
        bep_years = self.get_float_input("Break-even Point dalam tahun (desimal, contoh 2.45)")
        if bep_years == 'quit':
            return None
        if bep_years:
            data['bep_years'] = bep_years
        
        bep_km = self.get_float_input("Break-even Point dalam kilometer")
        if bep_km == 'quit':
            return None
        if bep_km:
            data['bep_km'] = bep_km
        
        # Cost structure
        self.print_markdown("### 🏗️ Struktur Biaya")
        
        owning_pct = self.get_float_input("Owning Cost (rasio 0-1, contoh 0.56)")
        if owning_pct == 'quit':
            return None
        if owning_pct is not None:
            data['owning_pct'] = owning_pct
        
        operational_pct = self.get_float_input("Operational Cost (rasio 0-1, contoh 0.44)")
        if operational_pct == 'quit':
            return None
        if operational_pct is not None:
            data['operational_pct'] = operational_pct
        
        residual_value_pct = self.get_float_input("Residual Value (rasio 0-1, contoh 0.30)")
        if residual_value_pct == 'quit':
            return None
        if residual_value_pct is not None:
            data['residual_value_pct'] = residual_value_pct
        
        # Check if we have enough data
        essential_fields = ['unit_name']
        if not any(field in data for field in essential_fields):
            self.print_markdown("### ❌ Minimal nama kendaraan harus diisi.")
            return self.collect_vehicle_data()
        
        return data
    
    def send_analysis_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Kirim request analisis ke API."""
        try:
            self.print_markdown("## 🔄 Menganalisis data kendaraan...")
            
            response = self.session.post(
                f"{self.api_url}/analyze",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_text = f"## ❌ Error API: Status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_text += f"\n**Error**: {error_data['error']}"
                except:
                    error_text += f"\n**Response**: {response.text}"
                
                self.print_markdown(error_text)
                return None
                
        except requests.exceptions.RequestException as e:
            self.print_markdown(f"## ❌ Request Gagal: {str(e)}")
            return None
    
    def display_analysis_results(self, response: Dict[str, Any]):
        """Tampilkan hasil analisis dengan format baru dari API."""
        self.print_markdown("# 🤖 Hasil Analisis ROI Kendaraan")
        
        # Check if response has error
        if 'error' in response:
            self.print_markdown(f"## ❌ Error: {response['error']}")
            return
        
        # Display ROI Analysis
        if 'roi' in response:
            roi = response['roi']
            roi_text = f"""
## 📈 ROI
**{roi.get('percentage', 'N/A')} – {roi.get('category', 'N/A')}**
{roi.get('short_sentence', '')}
{roi.get('insight_narrative', '')}
            """
            self.print_markdown(roi_text)
        
        # Display TCO Analysis
        if 'tco' in response:
            tco = response['tco']
            tco_text = f"""
## 💰 TCO
**{tco.get('amount_rp', 'N/A')} – {tco.get('category', 'N/A')}**
{tco.get('short_sentence', '')}
{tco.get('insight_narrative', '')}
            """
            self.print_markdown(tco_text)
        
        # Display Owning vs Operational Cost
        if 'owning_vs_operational' in response:
            cost_structure = response['owning_vs_operational']
            structure_text = f"""
## 🏗️ Owning vs Operational Cost
**Owning {cost_structure.get('owning_percentage', 'N/A')}% | Operational {cost_structure.get('operational_percentage', 'N/A')}% – {cost_structure.get('category', 'N/A')}**
{cost_structure.get('short_sentence', '')}
{cost_structure.get('cashflow_implication', '')}
(Pie chart placeholder)
            """
            self.print_markdown(structure_text)
        
        # Display Break Even Point
        if 'break_even_point' in response:
            bep = response['break_even_point']
            monthly_sim = bep.get('monthly_simulation', {})
            bep_text = f"""
## ⏱️ Break Even Point
**{bep.get('period', 'N/A')} | {bep.get('bep_km', 'N/A')} – {bep.get('category', 'N/A')}**
{bep.get('short_sentence', '')}

### Simulasi Bulanan:
- Cicilan: {monthly_sim.get('installment', 'N/A')}
- Revenue: {monthly_sim.get('revenue', 'N/A')}
- Net Cashflow: {monthly_sim.get('net_cashflow', 'N/A')}

{bep.get('bep_insight', '')}
            """
            self.print_markdown(bep_text)
        
        # Display Contribution Margin
        if 'contribution_margin_per_km' in response:
            margin = response['contribution_margin_per_km']
            margin_text = f"""
## 💎 Contribution Margin per KM
**{margin.get('margin_rp', 'N/A')} – {margin.get('category', 'N/A')}**
{margin.get('short_sentence', '')}
{margin.get('margin_insight', '')}
            """
            self.print_markdown(margin_text)
        
        # Display Overall Insight
        if 'overall_insight' in response:
            overall = response['overall_insight']
            overall_text = f"""
## 🎯 Overall Insight
{overall.get('summary', '')}
            """
            self.print_markdown(overall_text)
        
        # Display pie chart data if available
        if 'owning_vs_operational' in response and 'pie_chart_data' in response['owning_vs_operational']:
            pie_data = response['owning_vs_operational']['pie_chart_data']
            if RICH_AVAILABLE:
                table = Table(title="Distribusi Biaya")
                table.add_column("Kategori", style="cyan")
                table.add_column("Persentase", style="magenta")
                table.add_row("Owning Cost", f"{pie_data.get('owning_cost', 0)}%")
                table.add_row("Operational Cost", f"{pie_data.get('operational_cost', 0)}%")
                self.console.print(table)
        
        # Menu for additional options
        choice = self.show_menu([
            "Tampilkan response JSON lengkap", 
            "Kembali ke menu utama"
        ])
        
        if choice == 1:
            self.print_json(response, "🔍 Response API Lengkap")
    
    def run_analysis(self):
        """Jalankan sesi analisis."""
        data = self.collect_vehicle_data()
        if data is None or not data:
            return
        
        self.print_json(data, "📤 Data yang dikirim ke API")
        
        response = self.send_analysis_request(data)
        if response:
            self.display_analysis_results(response)
        else:
            self.print_markdown("## ❌ Tidak dapat mendapatkan response dari API")
    
    def run_json_analysis(self):
        """Jalankan sesi analisis dengan input JSON."""
        data = self.collect_json_input()
        if data is None or not data:
            return
        
        response = self.send_analysis_request(data)
        if response:
            self.display_analysis_results(response)
        else:
            self.print_markdown("## ❌ Tidak dapat mendapatkan response dari API")
    
    def show_sample_data(self):
        """Tampilkan contoh data untuk testing."""
        sample_data = {
            "unit_name": "Truk Hino 500",
            "segment": "Urban Logistics",
            "unit_price": 800000000,
            "uses_leasing": False,
            "tco": 1200000000,
            "annual_tco": 240000000,
            "cost_per_km": 5000,
            "revenue_per_km": 7500,
            "contribution_margin": 2500,
            "total_revenue": 1500000000,
            "roi": 1.15,
            "bep_years": 2.5,
            "bep_km": 150000,
            "owning_pct": 0.65,
            "operational_pct": 0.35,
            "residual_value_pct": 0.30
        }
        
        self.print_json(sample_data, "📋 Contoh Data Input")
        
        if RICH_AVAILABLE:
            use_sample = Confirm.ask("[green]Gunakan data contoh ini untuk analisis?[/green]")
        else:
            use_sample = input("Gunakan data contoh ini untuk analisis? (y/n): ").strip().lower() in ['y', 'yes', 'ya']
        
        if use_sample:
            response = self.send_analysis_request(sample_data)
            if response:
                self.display_analysis_results(response)
    
    def run(self):
        """Main entry point."""
        self.clear_screen()
        self.print_banner()
        
        # Check API connection first
        if not self.check_api_health():
            self.print_markdown("## ⚠️ API tidak tersedia. Pastikan server berjalan di http://localhost:8501")
            return
        
        # Main menu loop
        while True:
            try:
                choice = self.show_menu([
                    "Analisis ROI Kendaraan (Input Manual)",
                    "Analisis dengan Input JSON Lengkap",
                    "Analisis dengan Data Contoh",
                    "Cek Status API", 
                    "Keluar"
                ])
                
                if choice == 1:  # Manual Analysis
                    self.run_analysis()
                elif choice == 2:  # JSON Input Analysis
                    self.run_json_analysis()
                elif choice == 3:  # Sample Data Analysis
                    self.show_sample_data()
                elif choice == 4:  # Check API
                    self.check_api_health()
                elif choice == 5 or choice == -1:  # Exit
                    break
                
            except KeyboardInterrupt:
                break
        
        self.print_markdown("## 👋 Terima kasih telah menggunakan Vehicle ROI Analysis!")

def main():
    """Main function."""
    api_url = "http://localhost:8501"
    client = VehicleROITerminal(api_url)
    client.run()

if __name__ == "__main__":
    main()