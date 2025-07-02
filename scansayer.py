#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ScanSayer - ماسح أمني آلي مفتوح المصدر
المطور: Saudi Linux
البريد الإلكتروني: SayerLinux@gmail.com
"""

import argparse
import sys
import os
import time
from datetime import datetime
from colorama import init
from rich.console import Console
from rich.progress import Progress

# استيراد الوحدات الخاصة بالأداة
from modules.asset_discovery import AssetDiscovery
from modules.vulnerability_scanners import (
    WordPressScanner,
    CraftCMSScanner,
    SMBScanner,
    ZyxelScanner
)
from modules.report_generator import ReportGenerator

# تهيئة الألوان
init(autoreset=True)
console = Console()

# الإصدار الحالي
VERSION = "1.0.0"

class ScanSayer:
    def __init__(self, target, output=None, verbose=False, threads=10):
        self.target = target
        self.output = output
        self.verbose = verbose
        self.threads = threads
        self.results = {}
        self.start_time = time.time()
        self.scan_count = 0
        
        console.print(f"[bold green]بدء فحص الهدف: {self.target}[/bold green]")
        
    def run(self):
        """تشغيل جميع الفحوصات"""
        with Progress() as progress:
            task = progress.add_task("[cyan]جاري الفحص...", total=6)
            
            # 1. اكتشاف الأصول
            asset_discovery = AssetDiscovery(self.target, self.threads, self.verbose)
            discovery_results = asset_discovery.discover()
            self.results['hosts'] = discovery_results['hosts']
            self.results['ports'] = discovery_results['ports']
            self.results['web_services'] = discovery_results['web_services']
            self.scan_count += 1
            progress.update(task, advance=1)
            
            # 2. فحص ثغرات WordPress
            wp_scanner = WordPressScanner(self.target, self.verbose)
            self.results['wordpress'] = wp_scanner.scan(self.results['web_services'])
            self.scan_count += 1
            progress.update(task, advance=1)
            
            # 3. فحص ثغرات Craft CMS
            craft_scanner = CraftCMSScanner(self.target, self.verbose)
            self.results['craftcms'] = craft_scanner.scan(self.results['web_services'])
            self.scan_count += 1
            progress.update(task, advance=1)
            
            # 4. فحص ثغرات SMB
            smb_scanner = SMBScanner(self.target, self.verbose)
            # استخدام قائمة المنافذ المفتوحة للهدف الأول (في حالة وجود أكثر من هدف)
            first_host = self.results['hosts'][0] if self.results['hosts'] else self.target
            open_ports = self.results['ports'].get(first_host, [])
            self.results['smb'] = smb_scanner.scan(open_ports)
            self.scan_count += 1
            progress.update(task, advance=1)
            
            # 5. فحص ثغرات Zyxel
            zyxel_scanner = ZyxelScanner(self.target, self.verbose)
            self.results['zyxel'] = zyxel_scanner.scan(self.results['web_services'])
            self.scan_count += 1
            progress.update(task, advance=1)
            
            # 6. إنشاء التقرير
            scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            duration = time.time() - self.start_time
            report_generator = ReportGenerator(self.target, self.results, scan_time, duration)
            report_generator.display_console_report()
            
            # حفظ التقارير إذا تم تحديد ملف الإخراج
            if self.output:
                # حفظ تقرير JSON
                report_generator.save_json_report(self.output)
                
                # حفظ تقرير HTML
                html_output = os.path.splitext(self.output)[0] + '.html'
                report_generator.save_html_report(html_output)
            
            progress.update(task, advance=1)
            
        return self.results


def print_banner():
    """عرض شعار الأداة"""
    banner = f"""
    ███████╗ ██████╗ █████╗ ███╗   ██╗███████╗ █████╗ ██╗   ██╗███████╗██████╗ 
    ██╔════╝██╔════╝██╔══██╗████╗  ██║██╔════╝██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗
    ███████╗██║     ███████║██╔██╗ ██║███████╗███████║ ╚████╔╝ █████╗  ██████╔╝
    ╚════██║██║     ██╔══██║██║╚██╗██║╚════██║██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗
    ███████║╚██████╗██║  ██║██║ ╚████║███████║██║  ██║   ██║   ███████╗██║  ██║
    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                                            v{VERSION}
    ماسح أمني آلي مفتوح المصدر | المطور: Saudi Linux | SayerLinux@gmail.com
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")


def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # إعداد محلل الوسائط
    parser = argparse.ArgumentParser(description='ScanSayer - ماسح أمني آلي مفتوح المصدر')
    parser.add_argument('-t', '--target', required=True, help='الهدف للفحص (IP, نطاق CIDR, أو اسم المضيف)')
    parser.add_argument('-o', '--output', help='ملف لحفظ النتائج (JSON)')
    parser.add_argument('-v', '--verbose', action='store_true', help='عرض معلومات مفصلة')
    parser.add_argument('--threads', type=int, default=10, help='عدد مسارات التنفيذ المتوازية (الافتراضي: 10)')
    parser.add_argument('--version', action='version', version=f'ScanSayer v{VERSION}')
    
    args = parser.parse_args()
    
    try:
        # تجاهل تحذيرات SSL
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # بدء الفحص
        scanner = ScanSayer(
            target=args.target,
            output=args.output,
            verbose=args.verbose,
            threads=args.threads
        )
        scanner.run()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]تم إيقاف الفحص بواسطة المستخدم[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]خطأ: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == '__main__':
    main()