"""Check the shared UI palette against WCAG AA contrast thresholds."""
from pathlib import Path
import re


def luminance(color):
    components = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in components]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def ratio(foreground, background):
    values = sorted((luminance(foreground), luminance(background)))
    return (values[1] + 0.05) / (values[0] + 0.05)


def main():
    css = (Path(__file__).resolve().parents[1] / 'static/style.css').read_text(encoding='utf8')
    palette = dict(re.findall(r'--([a-z]+):(#[0-9a-f]{6})', css))
    star = re.search(r'\.stars\{color:(#[0-9a-f]{6})', css)[1]
    border = re.search(r'input,select,textarea\{[^}]*border:1px solid (#[0-9a-f]{6})', css)[1]
    backgrounds = [palette['paper'], palette['white'], '#eeeade', '#f5f0e4', '#f6e8b9', '#fffaf0']
    checks = []
    for label, foreground in [('body', palette['ink']), ('muted', palette['muted']),
                              ('accent', palette['red']), ('rating', star)]:
        for background in backgrounds:
            checks.append((label + ' on ' + background, ratio(foreground, background), 4.5))
    checks.extend([
        ('button text', ratio('#ffffff', palette['red']), 4.5),
        ('error text', ratio('#802014', '#fae3de'), 4.5),
        ('success text', ratio('#263b1f', '#e1ecd9'), 4.5),
        ('selected address', ratio('#261a13', '#f8d56b'), 4.5),
        ('control border', ratio(border, palette['white']), 3.0),
        ('control border against filter', ratio(border, '#eeeade'), 3.0),
        ('keyboard focus', ratio('#255b8b', palette['paper']), 3.0),
    ])
    for label, actual, threshold in checks:
        print(f'{label}: {actual:.2f}:1 (minimum {threshold}:1)')
    failures = [label for label, actual, threshold in checks if actual < threshold]
    if failures:
        raise SystemExit('Contrast failed: ' + ', '.join(failures))
    print(f'PASS: {len(checks)} shared-palette combinations. This is not a full accessibility audit.')


if __name__ == '__main__':
    main()
