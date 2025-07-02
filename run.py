#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ScanSayer - ماسح أمني آلي مفتوح المصدر
ملف تنفيذي للأداة
"""

import os
import sys
import subprocess

def check_requirements():
    """التحقق من تثبيت المتطلبات"""
    try:
        import colorama
        import rich
        return True
    except ImportError:
        print("[!] بعض المتطلبات غير مثبتة. جاري تثبيت المتطلبات...")
        return False

def install_requirements():
    """تثبيت المتطلبات"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("[+] تم تثبيت المتطلبات بنجاح!")
        return True
    except subprocess.CalledProcessError:
        print("[!] فشل في تثبيت المتطلبات. يرجى تثبيتها يدويًا باستخدام: pip install -r requirements.txt")
        return False

def main():
    """الدالة الرئيسية"""
    # التحقق من وجود Python 3
    if sys.version_info[0] < 3:
        print("[!] يتطلب ScanSayer Python 3. يرجى تشغيل الأداة باستخدام Python 3.")
        sys.exit(1)
    
    # التحقق من المتطلبات
    if not check_requirements():
        if not install_requirements():
            sys.exit(1)
    
    # تشغيل الأداة
    try:
        from scansayer import main as scansayer_main
        scansayer_main()
    except KeyboardInterrupt:
        print("\n[!] تم إيقاف الأداة بواسطة المستخدم.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] حدث خطأ: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()