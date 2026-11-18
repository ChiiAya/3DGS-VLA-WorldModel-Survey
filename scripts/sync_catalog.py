#!/usr/bin/env python3
"""Validate shared benchmark data and render README tables.

python3 scripts/sync_catalog.py --import-papers
python3 scripts/sync_catalog.py --site path/to/site
python3 scripts/sync_catalog.py --check

Edit data/catalog.json to add verified results. Paper metadata is imported from
the year-grouped README paper list only when --import-papers is requested.
The project website reads the public JSON and keeps a local fallback snapshot.
No third-party dependencies are required.
"""
from pathlib import Path
from html import unescape
import argparse
import json
import math
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def text(s):
    return unescape(re.sub('<[^>]*>', '', s)).strip()


def normalize(s):
    return re.sub('[^a-z0-9]', '', s.lower())


def find_url(s):
    m = re.search(r'\]\((https?://[^)]+)\)', s)
    return m[1] if m else ''


def import_papers(readme):
    papers = []
    year = 0
    for line in readme.split('## 📊')[0].splitlines():
        if re.fullmatch(r'### 20\d\d', line):
            year = int(line[4:])
        if not year or not line.startswith('|') or '<sub>' not in line:
            continue
        cells = [s.strip() for s in line.strip('|').split('|')]
        title = text(re.split(r'<br\s*/?>', cells[0])[0])
        authors = text(re.search(r'<sub>(.*?)</sub>', cells[0])[1])
        if any(normalize(p['title']) == normalize(title) for p in papers):
            continue
        papers.append(
            dict(
                title=title,
                authors=authors,
                venue=text(cells[1]),
                year=year,
                paper=find_url(cells[2]),
                code=find_url(cells[3]),
            )
        )
    return papers


def sync_publications(data):
    """Resolve explicit paper titles; method-name substring matching is unsafe."""
    papers = {p['title']: p for p in data['papers']}
    for group in data['benchmarks']:
        for row in group['rows']:
            if not row.get('paperTitle'):
                continue
            assert row['paperTitle'] in papers, (
                f"Unknown paper for {row['id']}: {row['paperTitle']}"
            )
            paper = papers[row['paperTitle']]
            venue = re.sub(r'(?<=\D)(20\d\d)$', r' \1', paper['venue']).strip()
            venue = re.sub(r'\s+', ' ', venue)
            if not re.search(r'20\d\d', venue):
                venue += f" {paper['year']}"
            row.update(venue=venue, paper=paper['paper'], code=paper['code'])


def validate(data):
    assert data['schemaVersion'] == 1
    assert len(data['benchmarks']) >= 1
    ids = set()
    for g in data['benchmarks']:
        for r in g['rows']:
            assert r['id'] not in ids, r['id']
            ids.add(r['id'])
            assert r['method'] and r['source'].startswith('https://')
            if g.get('tracks'):
                assert r['track'] in [t['id'] for t in g['tracks']]
            for c in g['columns']:
                val = r['scores'][c['id']]
                if isinstance(val, list):
                    assert len(val) in [2, 3]
                    assert all(isinstance(v, (int, float)) and math.isfinite(v) for v in val)
                    assert val[0] > 0 and 0 <= val[1] <= 1
                    if len(val) == 3:
                        assert val[2] >= 0
                else:
                    assert isinstance(val, (int, float)) and math.isfinite(val) and val >= 0
    assert data['paperCount'] == len(data['papers'])
    return len(ids)


def fmt_psnr_ssim_lpips(v):
    if len(v) == 3:
        return f'{v[0]:.2f}/{v[1]:.3f}/{v[2]:.3f}'
    return f'{v[0]:.2f}/{v[1]:.3f}'


def table(headers, rows):
    return '\n'.join(
        [
            '| ' + ' | '.join(headers) + ' |',
            '| ' + ' | '.join(['---'] * len(headers)) + ' |',
        ]
        + [
            '| ' + ' | '.join(str(c).replace('|', '&#124;') for c in row) + ' |'
            for row in rows
        ]
    )


def render_group(g):
    gid = g['id']
    if gid == 'waymo-notr':
        result = 'Metrics are **PSNR (↑) / SSIM (↑) / LPIPS (↓)** for full scenes and **PSNR* (↑) / SSIM* (↑)** for dynamic objects.\n\n'
        for track in g['tracks']:
            rows = [r for r in g['rows'] if r['track'] == track['id']]
            result += f"\n#### {track['label']}\n\n"
            headers = ['Method', 'Venue & Year'] + [c['label'] for c in g['columns']] + ['Notes']
            rendered_rows = [
                [
                    r['method'],
                    r['venue'],
                    fmt_psnr_ssim_lpips(r['scores']['full']),
                    fmt_psnr_ssim_lpips(r['scores']['dynamic']),
                    r['approach'],
                ]
                for r in rows
            ]
            result += table(headers, rendered_rows) + '\n'
        return result.strip() + '\n\n'

    if gid == 'waymo-novel-traj':
        result = 'Evaluated on lane-change novel trajectories on Waymo Open Dataset using **FID (↓)**.\n\n'
        headers = ['Method', 'Backbone / Base', 'Venue & Year', 'FID ↓', 'Approach']
        rendered_rows = [
            [
                r['method'],
                r['category'],
                r['venue'],
                f"{r['scores']['fid']:.2f}",
                r['approach'],
            ]
            for r in g['rows']
        ]
        return (result + table(headers, rendered_rows)).strip() + '\n\n'

    if gid == 'feedforward-3dgs':
        result = 'Two-view feed-forward 3DGS evaluation on RealEstate10K and zero-shot cross-dataset generalization on ACID. Metrics are **PSNR (↑) / SSIM (↑) / LPIPS (↓)**.\n\n'
        headers = ['Method', 'Venue & Year'] + [c['label'] for c in g['columns']] + ['Approach']
        rendered_rows = [
            [
                r['method'],
                r['venue'],
                fmt_psnr_ssim_lpips(r['scores']['re10k']),
                fmt_psnr_ssim_lpips(r['scores']['acid']),
                r['approach'],
            ]
            for r in g['rows']
        ]
        return (result + table(headers, rendered_rows)).strip() + '\n\n'

    if gid == 'lerf-open-vocab':
        result = 'Open-vocabulary 3D understanding on the LERF dataset across *Ramen*, *Figurines*, *Teatime*, and *Waldo Kitchen*. Higher is better (↑).\n\n'
        for track in g['tracks']:
            rows = [r for r in g['rows'] if r['track'] == track['id']]
            result += f"\n#### {track['label']}\n\n"
            headers = ['Method', 'Venue & Year', 'Metric'] + [c['label'] for c in g['columns']]
            rendered_rows = [
                [
                    r['method'],
                    r['venue'],
                    r['category'],
                    f"{r['scores']['ramen']:.1f}",
                    f"{r['scores']['figurines']:.1f}",
                    f"{r['scores']['teatime']:.1f}",
                    f"{r['scores']['kitchen']:.1f}",
                    f"{r['scores']['overall']:.1f}",
                ]
                for r in rows
            ]
            result += table(headers, rendered_rows) + '\n'
        return result.strip() + '\n\n'

    result = 'Evaluated across 10 multi-task language-conditioned RLBench tasks (166 variations). Metric is **Average Success Rate (%) ↑**.\n\n'
    headers = ['Category', 'Method', 'Venue & Year', 'Avg. Success Rate (%) ↑', 'Approach']
    rendered_rows = [
        [
            r['category'],
            r['method'],
            r['venue'],
            f"{r['scores']['avg_sr']:.1f}",
            r['approach'],
        ]
        for r in g['rows']
    ]
    return (result + table(headers, rendered_rows)).strip() + '\n\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--check',
        action='store_true',
        help='validate and fail if generated tables or snapshot differ',
    )
    parser.add_argument(
        '--import-papers',
        action='store_true',
        help='refresh paper metadata from the README year tables',
    )
    parser.add_argument(
        '--site',
        type=Path,
        help='optional site directory for the local JS snapshot',
    )
    args = parser.parse_args()

    readme = (ROOT / 'README.md').read_text(encoding='utf8')
    data = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf8'))
    original_data = json.loads(json.dumps(data))

    if args.import_papers:
        data['papers'] = import_papers(readme)
        data['paperCount'] = len(data['papers'])

    sync_publications(data)
    count = validate(data)

    rendered = readme
    for g in data['benchmarks']:
        heading = g['title']
        pattern = r'(### ' + re.escape(heading) + r'\s*\n).*?(?=\n### |\n## |\Z)'
        rendered, n = re.subn(
            pattern,
            lambda m, g=g, heading=heading: '### ' + heading + '\n\n' + render_group(g),
            rendered,
            flags=re.S,
        )
        assert n == 1, heading

    snapshot = (
        'window.SURVEY_CATALOG = '
        + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        + ';\n'
    )

    if args.check:
        if data != original_data:
            sys.exit('Paper and benchmark publication metadata differ; run scripts/sync_catalog.py')
        if readme != rendered:
            sys.exit('README benchmark tables differ; run scripts/sync_catalog.py')
        if args.site and (args.site / 'catalog.js').read_text(encoding='utf8') != snapshot:
            sys.exit('Website fallback differs; run sync with --site')
    else:
        (ROOT / 'data/catalog.json').write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8'
        )
        (ROOT / 'README.md').write_text(rendered, encoding='utf8')
        if args.site:
            assert args.site.is_dir(), args.site
            (args.site / 'catalog.js').write_text(snapshot, encoding='utf8')

    print(
        f"Validated {len(data['papers'])} papers and {count} results across {len(data['benchmarks'])} benchmark families."
    )


if __name__ == '__main__':
    main()
