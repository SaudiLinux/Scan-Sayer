#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة إنشاء التقارير لـ ScanSayer
المطور: Saudi Linux
البريد الإلكتروني: SayerLinux@gmail.com
"""

import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

# تهيئة وحدة الطباعة الغنية
console = Console()

class ReportGenerator:
    """فئة إنشاء التقارير"""
    
    def __init__(self, target, results, scan_time, duration):
        self.target = target
        self.results = results
        self.scan_time = scan_time
        self.duration = duration
        self.vuln_count = self._count_vulnerabilities()
    
    def _count_vulnerabilities(self):
        """حساب عدد الثغرات المكتشفة"""
        count = 0
        
        # WordPress
        for vuln in self.results.get('wordpress', []):
            if vuln.get('vulnerable', False):
                count += 1
        
        # Craft CMS
        for vuln in self.results.get('craftcms', []):
            if vuln.get('vulnerable', False):
                count += 1
        
        # SMB
        for vuln in self.results.get('smb', []):
            if vuln.get('vulnerable', False):
                count += 1
        
        # Zyxel
        for vuln in self.results.get('zyxel', []):
            if vuln.get('vulnerable', False):
                count += 1
        
        return count
    
    def display_console_report(self):
        """عرض تقرير في وحدة التحكم"""
        console.print("\n[bold green]===== تقرير الفحص =====[/bold green]")
        console.print(f"[bold]الهدف:[/bold] {self.target}")
        console.print(f"[bold]وقت الفحص:[/bold] {self.scan_time}")
        console.print(f"[bold]المدة:[/bold] {self.duration:.2f} ثانية")
        console.print(f"[bold]عدد الثغرات المكتشفة:[/bold] {self.vuln_count}")
        
        if self.vuln_count > 0:
            table = Table(title="الثغرات المكتشفة")
            table.add_column("النوع", style="cyan")
            table.add_column("الهدف", style="green")
            table.add_column("التفاصيل", style="red")
            
            # WordPress
            for vuln in self.results.get('wordpress', []):
                if vuln.get('vulnerable', False):
                    table.add_row("WordPress", vuln['url'], vuln['details'])
            
            # Craft CMS
            for vuln in self.results.get('craftcms', []):
                if vuln.get('vulnerable', False):
                    table.add_row("Craft CMS", vuln['url'], f"{vuln['details']} (الإصدار {vuln['version']})")
            
            # SMB
            for vuln in self.results.get('smb', []):
                if vuln.get('vulnerable', False):
                    table.add_row("SMB", f"{vuln['host']} ({vuln['share']})", vuln['details'])
            
            # Zyxel
            for vuln in self.results.get('zyxel', []):
                if vuln.get('vulnerable', False):
                    table.add_row("Zyxel", vuln['url'], vuln['details'])
            
            console.print(table)
        else:
            console.print("[bold blue]لم يتم اكتشاف أي ثغرات![/bold blue]")
    
    def save_json_report(self, output_file):
        """حفظ التقرير بتنسيق JSON"""
        try:
            output_data = {
                'target': self.target,
                'scan_time': self.scan_time,
                'duration': f"{self.duration:.2f} seconds",
                'vuln_count': self.vuln_count,
                'results': self.results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            
            console.print(f"\n[bold green]تم حفظ التقرير في: {output_file}[/bold green]")
            return True
        except Exception as e:
            console.print(f"\n[bold red]خطأ في حفظ التقرير: {str(e)}[/bold red]")
            return False
    
    def save_html_report(self, output_file):
        """حفظ التقرير بتنسيق HTML"""
        try:
            # إنشاء قالب HTML بسيط
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>تقرير فحص ScanSayer - {self.target}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
                    h1, h2 {{ color: #2c3e50; }}
                    .header {{ background-color: #3498db; color: white; padding: 10px; border-radius: 5px; }}
                    .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .vuln-high {{ color: #e74c3c; }}
                    .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #7f8c8d; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>تقرير فحص ScanSayer</h1>
                </div>
                
                <div class="summary">
                    <h2>ملخص الفحص</h2>
                    <p><strong>الهدف:</strong> {self.target}</p>
                    <p><strong>وقت الفحص:</strong> {self.scan_time}</p>
                    <p><strong>المدة:</strong> {self.duration:.2f} ثانية</p>
                    <p><strong>عدد الثغرات المكتشفة:</strong> {self.vuln_count}</p>
                </div>
            """
            
            if self.vuln_count > 0:
                html_content += """
                <div class="vulnerabilities">
                    <h2>الثغرات المكتشفة</h2>
                    <table>
                        <tr>
                            <th>النوع</th>
                            <th>الهدف</th>
                            <th>التفاصيل</th>
                        </tr>
                """
                
                # WordPress
                for vuln in self.results.get('wordpress', []):
                    if vuln.get('vulnerable', False):
                        html_content += f"""
                        <tr>
                            <td>WordPress</td>
                            <td>{vuln['url']}</td>
                            <td class="vuln-high">{vuln['details']}</td>
                        </tr>
                        """
                
                # Craft CMS
                for vuln in self.results.get('craftcms', []):
                    if vuln.get('vulnerable', False):
                        html_content += f"""
                        <tr>
                            <td>Craft CMS</td>
                            <td>{vuln['url']}</td>
                            <td class="vuln-high">{vuln['details']} (الإصدار {vuln['version']})</td>
                        </tr>
                        """
                
                # SMB
                for vuln in self.results.get('smb', []):
                    if vuln.get('vulnerable', False):
                        html_content += f"""
                        <tr>
                            <td>SMB</td>
                            <td>{vuln['host']} ({vuln['share']})</td>
                            <td class="vuln-high">{vuln['details']}</td>
                        </tr>
                        """
                
                # Zyxel
                for vuln in self.results.get('zyxel', []):
                    if vuln.get('vulnerable', False):
                        html_content += f"""
                        <tr>
                            <td>Zyxel</td>
                            <td>{vuln['url']}</td>
                            <td class="vuln-high">{vuln['details']}</td>
                        </tr>
                        """
                
                html_content += """
                    </table>
                </div>
                """
            else:
                html_content += """
                <div class="no-vulnerabilities">
                    <h2>نتائج الفحص</h2>
                    <p>لم يتم اكتشاف أي ثغرات!</p>
                </div>
                """
            
            html_content += f"""
                <div class="footer">
                    <p>تم إنشاء هذا التقرير بواسطة ScanSayer - ماسح أمني آلي مفتوح المصدر</p>
                    <p>المطور: Saudi Linux | البريد الإلكتروني: SayerLinux@gmail.com</p>
                </div>
            </body>
            </html>
            """
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            console.print(f"\n[bold green]تم حفظ التقرير HTML في: {output_file}[/bold green]")
            return True
        except Exception as e:
            console.print(f"\n[bold red]خطأ في حفظ التقرير HTML: {str(e)}[/bold red]")
            return False