# ScanSayer

ماسح أمني آلي مفتوح المصدر مصمم لاكتشاف الأصول وفحص الثغرات الأمنية. تستخدم الأداة أحدث الأدوات والتقنيات مفتوحة المصدر لأداء هذه المهام.

## الميزات

- اكتشاف الأصول في الشبكة المستهدفة
- فحص الثغرات الأمنية المعروفة
- تقارير مفصلة عن نتائج الفحص
- واجهة سهلة الاستخدام

## الثغرات المكتشفة

تستطيع الأداة اكتشاف الثغرات التالية:

- Wordpress TemplateInvaders - Arbitrary File Upload
- Craft CMS - Remote Code Execution
- SMB - Anonymous Write Access
- Zyxel - Default credentials

## المتطلبات

- Python 3.8+
- نظام تشغيل: Windows, Linux, macOS

## التثبيت

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل الأداة
python scansayer.py -h
```

## الاستخدام

```bash
python scansayer.py -t [target] -o [output_file]
```

## المساهمة

nالمساهمات مرحب بها! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) للحصول على مزيد من المعلومات.

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للحصول على التفاصيل.

## المطور

- Saudi Linux
- البريد الإلكتروني: SayerLinux@gmail.com