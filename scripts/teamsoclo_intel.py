#!/usr/bin/env python3
# SV-SUPPLY-3: Deep passive OSINT on teamsoclo.site (public GET only)
import json, re, socket, ssl
from datetime import datetime, timezone
import requests, urllib3
urllib3.disable_warnings()

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      'Accept': 'text/html,application/json,*/*'}
res = {'generated': datetime.now(timezone.utc).isoformat(), 'target': 'teamsoclo.site'}

# ============ 1. DNS ============
subs = ['teamsoclo.site', 'gpt.teamsoclo.site', 'redeem.teamsoclo.site', 'docs.teamsoclo.site',
        'api.teamsoclo.site', 'www.teamsoclo.site', 'panel.teamsoclo.site', 'dashboard.teamsoclo.site']
res['dns'] = {}
for h in subs:
    try:
        ips = sorted({ai[4][0] for ai in socket.getaddrinfo(h, 443, socket.AF_INET)})
        info = {'ips': ips}
        try:
            info['reverse'] = socket.gethostbyaddr(ips[0])[0]
        except Exception:
            info['reverse'] = None
        res['dns'][h] = info
    except Exception as e:
        res['dns'][h] = {'error': 'NXDOMAIN/unresolved'}

# ============ 2. HTTP probing ============
def get(url, t=20):
    try:
        r = requests.get(url, headers=UA, timeout=(5, t), verify=False, allow_redirects=True)
        return {'status': r.status_code, 'final_url': r.url,
                'server': r.headers.get('server',''), 'powered': r.headers.get('x-powered-by',''),
                'cf_ray': r.headers.get('cf-ray',''), 'title': (re.search(r'<title[^>]*>(.*?)</title>', r.text[:5000], re.S|re.I).group(1).strip()[:100] if re.search(r'<title[^>]*>(.*?)</title>', r.text[:5000], re.S|re.I) else ''),
                'body_head': (r.text or '')[:1500], 'size': len(r.text or ''),
                'headers': {k: v for k, v in r.headers.items() if k.lower() in ('server','x-powered-by','cf-ray','content-type','location','set-cookie')}}
    except Exception as e:
        return {'status': 0, 'error': str(e)[:120]}

res['http'] = {}
res['http']['root'] = get('https://teamsoclo.site/')
res['http']['gpt'] = get('https://gpt.teamsoclo.site/')
res['http']['gpt_v1'] = get('https://gpt.teamsoclo.site/v1/models')
res['http']['gpt_check'] = get('https://gpt.teamsoclo.site/check')
res['http']['redeem'] = get('https://redeem.teamsoclo.site/')
res['http']['docs'] = get('https://docs.teamsoclo.site/')

# ============ 3. TLS certificate (issuer, SANs, dates) ============
try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection(('teamsoclo.site', 443), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname='teamsoclo.site') as s:
            cert = s.getpeercert(binary_form=True)
    import subprocess
    pem = ssl.DER_cert_to_PEM_cert(cert)
    open('/tmp/tsc.pem','w').write(pem)
    out = subprocess.run(['openssl','x509','-in','/tmp/tsc.pem','-noout','-subject','-issuer','-dates','-ext','subjectAltName'],
                         capture_output=True, text=True).stdout
    res['tls'] = out.strip()
except Exception as e:
    res['tls'] = f'error: {str(e)[:120]}'

# ============ 4. Telegram presence ============
res['telegram'] = {}
for u in ['https://t.me/teamsoclo', 'https://t.me/s/teamsoclo']:
    r = get(u, 15)
    if r['status']:
        body = r.get('body_head','')
        m = re.search(r'<meta property="og:description" content="([^"]+)"', body)
        t = re.search(r'<meta property="og:title" content="([^"]+)"', body)
        res['telegram'][u] = {'status': r['status'], 'title': t.group(1) if t else r.get('title',''),
                              'og_description': m.group(1)[:400] if m else ''}
        # grab message preview from t.me/s/
        if '/s/' in u and r['status'] == 200:
            full = requests.get(u, headers=UA, timeout=(5,15), verify=False).text
            msgs = re.findall(r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', full, re.S)[:8]
            import html as H
            res['telegram']['preview_messages'] = [H.unescape(re.sub(r'<[^>]+>',' ',m)).strip()[:300] for m in msgs]

json.dump(res, open('/home/z/my-project/research/stackvault_live/teamsoclo_intel.json','w'), ensure_ascii=False, indent=1)
# print condensed
cond = {'dns': res['dns'], 'http': {k: {kk: vv for kk, vv in v.items() if kk != 'body_head'} for k, v in res['http'].items()},
        'tls': res.get('tls','')[:500], 'telegram': res.get('telegram',{})}
print(json.dumps(cond, ensure_ascii=False, indent=1)[:5000])
