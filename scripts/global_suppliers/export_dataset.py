#!/usr/bin/env python3
# GDS-1: Export master dataset (JSON + CSV + Arabic MD summary) to download/
import json, csv, os
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'
DL = '/home/z/my-project/download'

def main():
    ents = json.load(open(f'{GS}/entities/qualified.json'))
    nq = json.load(open(f'{GS}/entities/non_qualified.json'))
    state = json.load(open(f'{GS}/state.json'))
    now = datetime.now(timezone.utc).isoformat(timespec='minutes')

    # 1. Master JSON (full schema + evidence)
    master = {
        'dataset': 'MASTER_GDS_DATASET (run GDS-1)',
        'generated': now,
        'target': 1000,
        'unique_qualified_entity_count': len(ents),
        'progress_pct': round(100*len(ents)/1000, 1),
        'status': 'IN PROGRESS — session checkpoint (search-quota bounded)',
        'entities': ents,
    }
    json.dump(master, open(f'{DL}/gds_qualified_entities.json','w'), ensure_ascii=False, indent=1)

    # 2. CSV (flat, for analysis)
    cols = ['Entity_ID','Canonical_Name','Official_Domain','Country','Region','Entity_Type','Business_Model',
            'Digital_Categories','B2B','Wholesale','Reseller','API','Webhook','H2H','White_Label',
            'Automated_Fulfillment','Catalog_Breadth','Geographic_Coverage','Confidence','Last_Checked','Notes']
    with open(f'{DL}/gds_qualified_entities.csv','w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for e in ents:
            w.writerow([e.get(c,'') for c in cols[:-1]] + [ (e.get('Notes','') or '')[:200]])

    # 3. Arabic readable summary
    types, regions, confs = {}, {}, {}
    for e in ents:
        types[e['Entity_Type']] = types.get(e['Entity_Type'],0)+1
        regions[e['Region']] = regions.get(e['Region'],0)+1
        confs[e['Confidence']] = confs.get(e['Confidence'],0)+1
    lines = [
        '# مجموعة بيانات موردي المنتجات الرقمية العالميين — سجل الجلسة GDS-1',
        f'**تاريخ الإنشاء:** {now}',
        '',
        f'## العداد الرسمي: UNIQUE_QUALIFIED_ENTITY_COUNT = **{len(ents)}** / الهدف 1000 ({master["progress_pct"]}%)',
        '',
        '## ملخص التوزيع',
        f'- **حسب النوع:** ' + ' · '.join(f'{k}: {v}' for k,v in sorted(types.items(), key=lambda x:-x[1])),
        f'- **حسب المنطقة:** ' + ' · '.join(f'{k}: {v}' for k,v in sorted(regions.items(), key=lambda x:-x[1])),
        f'- **حسب الثقة:** ' + ' · '.join(f'{k}: {v}' for k,v in confs.items()),
        f'- مرفوضة (بعد المراجعة اليدوية): {len(nq.get("rejected",[]))} | أدلة غير كافية: {len(nq.get("insufficient",[]))}',
        '',
        '## قائمة الكيانات المؤهلة (الاسم — النطاق — النوع — الثقة)',
    ]
    for e in ents:
        lines.append(f"- **{e['Canonical_Name'][:50]}** — `{e['Official_Domain']}` — {e['Entity_Type']} — {e['Confidence']}")
    lines += [
        '',
        '## حدود البحث القادمة (NEXT SEARCH FRONTIER)',
        '- استكمال استعلامات الخطة المتبقية (99 من 262) — الإقليمية المحلية ذات الأولوية',
        '- مناطق غير مفحوصة بعد: اليابان/كوريا المحلية، الصين (فيتنام/كمبوديا)، آسيا الوسطى، القوقاز، سريلانكا',
        '- طبقات لم تُستكشف: موزعو البرمجيات المؤسسية (VAR)، شبكات البطاقات عبر الهاتف (carrier billing)، موزعو الكوبونات/الخصومات',
        '- لغات لم تُستخدم: اليابانية بعمق، الكورية، الفارسية/الأردية، السواحيلية',
        '- القناة الحرة المجدولة: حصادة مقالات القوائم + خرائط المواقع للكيانات الجديدة (لا تستهلك حصة البحث)',
        '',
        '## ملاحظات المنهجية والأمانة',
        '- كل كيان مؤهل له نطاق رسمي تم التحقق منه مباشرة عبر HTTP (أو دليل مقتطف من نطاقه الرسمي عند الحجب)',
        '- الثقة HIGH = إشارات B2B + فئات رقمية ظاهرة على صفحة النطاق الرسمي نفسها',
        '- الثقة MEDIUM = دليل من نطاقه الرسمي عبر نتائج البحث (صفحة محجوبة آليًا أو SPA)',
        '- لم يُختلق أي نطاق أو دليل؛ المرفوضات والأدلة غير الكافية مسجلة بالسبب',
    ]
    open(f'{DL}/gds_dataset_summary_ar.md','w',encoding='utf-8').write('\n'.join(lines))

    # 4. state checkpoint update
    state['checkpoint'] = {
        'qualified_total': len(ents), 'last_checkpoint_at': now,
        'checkpoint_number': len(ents)//100,
        'note': f'{len(ents)} qualified — session checkpoint; resumable via queries ledger + frontier',
    }
    state['counters'] = {**state.get('counters',{}), 'qualified_new': len(ents)}
    state['persistence'] = {
        'LAST VERIFIED STATE': f'{len(ents)} qualified; {state["counters"].get("queries_ok",0)} search queries OK; 624+ domains page-verified',
        'QUALIFIED ENTITIES': 'research/global_suppliers/entities/qualified.json',
        'DUPLICATES/REJECTED': 'research/global_suppliers/entities/non_qualified.json + qc_rejects.json',
        'INSUFFICIENT EVIDENCE': 'research/global_suppliers/entities/non_qualified.json (insufficient)',
        'RESEARCH FRONTIER': 'download/gds_dataset_summary_ar.md (NEXT SEARCH FRONTIER section)',
        'NEXT WORK': 'run discover.mjs for remaining 99 queries -> process -> verify_chunked -> qualify --rebuild -> qc_apply; then new query wave for uncovered regions',
    }
    json.dump(state, open(f'{GS}/state.json','w'), ensure_ascii=False, indent=1)

    print(f"Exported: {DL}/gds_qualified_entities.json (full schema)")
    print(f"Exported: {DL}/gds_qualified_entities.csv ({len(ents)} rows)")
    print(f"Exported: {DL}/gds_dataset_summary_ar.md (Arabic summary + frontier)")

if __name__ == '__main__':
    main()
