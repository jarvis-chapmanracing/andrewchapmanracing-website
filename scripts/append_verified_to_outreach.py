#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SHEET_ID = '13hL8yqYgt_5s8k879T0eyVbSm_r2WkUEYSxI0xCyVK0'
TAB = 'Outreach Log'
ROOT = Path('/home/andre/.openclaw/workspace')
VERIFIED = ROOT / 'lead_data' / 'verified research'

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d\s\-\(\)]{6,}\d")
LINKEDIN = re.compile(r'https?://[^\s]*linkedin\.com/\S*', re.I)
INSTAGRAM = re.compile(r'https?://[^\s]*instagram\.com/\S*', re.I)


def gs_get(range_name: str):
    url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(range_name, safe="")}'
    req = urllib.request.Request(url)
    req.add_header('Authorization', f"Bearer {os.environ['MATON_API_KEY']}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def gs_append(rows):
    url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(TAB, safe="")}:append?valueInputOption=USER_ENTERED'
    req = urllib.request.Request(url, data=json.dumps({'values': rows}).encode(), method='POST')
    req.add_header('Authorization', f"Bearer {os.environ['MATON_API_KEY']}")
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def field(lines, label):
    prefix = f'- **{label}:**'
    for line in lines:
        if line.startswith(prefix):
            return line.split(':', 1)[1].strip()
    return ''


def parse_contacts(text):
    sec = ''
    if '## 4.' in text:
        sec = text.split('## 4.', 1)[1]
        if '## 5.' in sec:
            sec = sec.split('## 5.', 1)[0]
    blocks, cur = [], []
    for line in sec.splitlines():
        if line.startswith('- **'):
            if cur:
                blocks.append(cur)
            cur = [line]
        elif cur:
            cur.append(line)
    if cur:
        blocks.append(cur)
    return blocks


def parse_block(block):
    txt = '\n'.join(block)
    name = field(block, 'Name') or field(block, 'Name & title')
    title = field(block, 'Title')
    if name and ' / ' in name and not title:
        name, title = name.split(' / ', 1)
    if not name and block:
        m = re.match(r'- \*\*(.*?)\*\*', block[0])
        if m:
            hdr = m.group(1).strip()
            if hdr.lower() not in {'name', 'name & title', 'contact', 'primary', 'secondary'}:
                if ' / ' in hdr:
                    name, title = hdr.split(' / ', 1)
                else:
                    name = hdr
    emails = EMAIL.findall(txt)
    phones = PHONE.findall(txt)
    links = LINKEDIN.findall(txt)
    igs = INSTAGRAM.findall(txt)
    channel = 'Email' if emails else ('LinkedIn' if links else ('Phone' if phones else ''))
    return [
        (name or '').strip(),
        (title or '').strip(),
        (emails[0] if emails else '').strip(),
        (phones[0] if phones else '').strip(),
        (igs[0] if igs else '').strip(),
        (links[0] if links else '').strip(),
        channel,
    ]


def existing_paths():
    values = gs_get(f'{TAB}!A1:U').get('values', [])
    return {row[20] for row in values[1:] if len(row) > 20}


def make_row(path: Path):
    txt = path.read_text(errors='ignore')
    lines = txt.splitlines()
    company = field(lines, 'Name') or path.stem
    stage = field(lines, 'Stage') or ('Pitch-ready' if 'Pitch-ready' in txt else 'Vetted')
    notes = []
    for label in ['Important notes/follow-ups', 'Next steps']:
        val = field(lines, label)
        if val:
            notes.append(val)
    contacts = parse_contacts(txt)
    primary = ['', '', '', '', '', '', '']
    secondary = ['', '', '', '', '', '', '']
    if contacts:
        primary = parse_block(contacts[0])
    if len(contacts) > 1:
        secondary = parse_block(contacts[1])
    best = 'Email' if primary[2] else ('Phone' if primary[3] else ('LinkedIn' if primary[5] else ''))
    return [company, *primary, *secondary, best, stage, '', '', ' | '.join(notes), str(path.resolve())]


def main():
    if 'MATON_API_KEY' not in os.environ:
        print('MATON_API_KEY missing', file=sys.stderr)
        return 1
    sheet_paths = existing_paths()
    files = sorted(p for p in VERIFIED.glob('*.md') if str(p.resolve()) not in sheet_paths)
    rows = [make_row(p) for p in files]
    if not rows:
        print('Appended 0 rows')
        return 0
    gs_append(rows)
    print(f'Appended {len(rows)} rows')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
