#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة اكتشاف الأصول لـ ScanSayer
المطور: Saudi Linux
البريد الإلكتروني: SayerLinux@gmail.com
"""

import socket
import ipaddress
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from rich.console import Console

# تهيئة وحدة الطباعة الغنية
console = Console()

# إعداد وكيل المستخدم العشوائي
ua = UserAgent()

# التحقق من وجود nmap
def is_nmap_installed():
    """التحقق من وجود nmap على النظام"""
    try:
        # محاولة استيراد مكتبة nmap
        import nmap
        
        # محاولة تنفيذ أمر nmap للتحقق من وجوده
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(['where', 'nmap'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # Linux/Mac
            result = subprocess.run(['which', 'nmap'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return result.returncode == 0
    except (ImportError, FileNotFoundError):
        return False

class AssetDiscovery:
    """فئة اكتشاف الأصول في الشبكة"""
    
    def __init__(self, target, threads=10, verbose=False):
        self.target = target
        self.threads = threads
        self.verbose = verbose
        self.hosts = []
        self.ports = {}
        self.web_services = []
        self.nmap_available = is_nmap_installed()
    
    def discover(self):
        """اكتشاف الأصول في الشبكة المستهدفة"""
        console.print("\n[bold blue]بدء اكتشاف الأصول...[/bold blue]")
        
        # تحديد نطاق الأهداف
        self._identify_targets()
        
        # فحص المنافذ المفتوحة
        self._scan_ports()
        
        # اكتشاف خدمات الويب
        self._discover_web_services()
        
        return {
            'hosts': self.hosts,
            'ports': self.ports,
            'web_services': self.web_services
        }
    
    def _identify_targets(self):
        """تحديد الأهداف للفحص"""
        try:
            if '/' in self.target:
                # CIDR notation
                network = ipaddress.ip_network(self.target, strict=False)
                self.hosts = [str(ip) for ip in network.hosts()]
                console.print(f"  [green]تم تحديد {len(self.hosts)} هدف في النطاق {self.target}[/green]")
            else:
                # Single IP or hostname
                ip = socket.gethostbyname(self.target)
                self.hosts = [ip]
                console.print(f"  [green]تم تحديد الهدف: {ip}[/green]")
        except (socket.gaierror, ValueError) as e:
            console.print(f"  [bold red]خطأ في تحديد الأهداف: {str(e)}[/bold red]")
    
    def _scan_ports(self):
        """فحص المنافذ المفتوحة"""
        console.print("\n[bold blue]فحص المنافذ المفتوحة...[/bold blue]")
        
        if self.nmap_available:
            self._scan_ports_with_nmap()
        else:
            console.print("  [yellow]nmap غير متوفر، سيتم استخدام طريقة بديلة لفحص المنافذ[/yellow]")
            self._scan_ports_with_socket()
    
    def _scan_ports_with_nmap(self):
        """فحص المنافذ المفتوحة باستخدام nmap"""
        try:
            import nmap
            nm = nmap.PortScanner()
            
            for host in self.hosts:
                try:
                    console.print(f"  [cyan]فحص المنافذ للهدف: {host}[/cyan]")
                    nm.scan(host, arguments='-sS -sV -T4 --top-ports 1000')
                    
                    self.ports[host] = []
                    
                    for proto in nm[host].all_protocols():
                        lport = sorted(nm[host][proto].keys())
                        for port in lport:
                            service = nm[host][proto][port]
                            port_info = {
                                'port': port,
                                'state': service['state'],
                                'service': service['name'],
                                'version': service.get('product', '') + ' ' + service.get('version', '')
                            }
                            
                            self.ports[host].append(port_info)
                            
                            if self.verbose and service['state'] == 'open':
                                console.print(f"    [green]المنفذ {port}/{proto}: {service['name']} {service.get('product', '')} {service.get('version', '')}[/green]")
                except Exception as e:
                    console.print(f"    [bold red]خطأ في فحص المنافذ للهدف {host}: {str(e)}[/bold red]")
        except ImportError:
            console.print("  [bold red]خطأ في استيراد مكتبة nmap[/bold red]")
            self._scan_ports_with_socket()
    
    def _scan_ports_with_socket(self):
        """فحص المنافذ المفتوحة باستخدام socket"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
        
        for host in self.hosts:
            console.print(f"  [cyan]فحص المنافذ للهدف: {host}[/cyan]")
            self.ports[host] = []
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self._check_port, host, port): port for port in common_ports}
                
                for future in futures:
                    port = futures[future]
                    try:
                        result = future.result()
                        if result:
                            port_info = {
                                'port': port,
                                'state': 'open',
                                'service': self._get_service_name(port),
                                'version': ''
                            }
                            self.ports[host].append(port_info)
                            
                            if self.verbose:
                                console.print(f"    [green]المنفذ {port}/tcp: {port_info['service']}[/green]")
                    except Exception as e:
                        if self.verbose:
                            console.print(f"    [red]خطأ في فحص المنفذ {port}: {str(e)}[/red]")
    
    def _check_port(self, host, port):
        """التحقق من حالة منفذ محدد"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    
    def _get_service_name(self, port):
        """الحصول على اسم الخدمة بناءً على رقم المنفذ"""
        services = {
            21: 'ftp',
            22: 'ssh',
            23: 'telnet',
            25: 'smtp',
            53: 'domain',
            80: 'http',
            110: 'pop3',
            111: 'rpcbind',
            135: 'msrpc',
            139: 'netbios-ssn',
            143: 'imap',
            443: 'https',
            445: 'microsoft-ds',
            993: 'imaps',
            995: 'pop3s',
            1723: 'pptp',
            3306: 'mysql',
            3389: 'ms-wbt-server',
            5900: 'vnc',
            8080: 'http-proxy',
            8443: 'https-alt'
        }
        return services.get(port, 'unknown')
    
    def _discover_web_services(self):
        """اكتشاف خدمات الويب"""
        console.print("\n[bold blue]اكتشاف خدمات الويب...[/bold blue]")
        
        web_ports = [80, 443, 8080, 8443]
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for host in self.hosts:
                for port in web_ports:
                    executor.submit(self._check_web_service, host, port)
    
    def _check_web_service(self, host, port):
        """فحص خدمة ويب على منفذ محدد"""
        try:
            url = f"http://{host}:{port}" if port != 443 else f"https://{host}"
            headers = {'User-Agent': ua.random}
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                server = response.headers.get('Server', 'Unknown')
                title = self._extract_title(response.text)
                
                web_service = {
                    'url': url,
                    'status': response.status_code,
                    'server': server,
                    'title': title
                }
                
                self.web_services.append(web_service)
                
                if self.verbose:
                    console.print(f"  [green]خدمة ويب: {url} | Server: {server} | Title: {title}[/green]")
        except requests.exceptions.RequestException:
            pass
    
    def _extract_title(self, html):
        """استخراج عنوان الصفحة من HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.title.string.strip() if soup.title else 'No Title'
        except:
            return 'No Title'