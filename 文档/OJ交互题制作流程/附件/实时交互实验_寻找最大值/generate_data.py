from pathlib import Path
import json
import random

ROOT = Path(__file__).resolve().parent


def main():
    rng = random.Random(20260914)
    cases = [([2, 1], '最小规模，最大值在左'), ([1, 2], '最小规模，最大值在右'),
             ([2, 5, 1, 4, 3], '样例，次大值与最大值分处不同半区'),
             ([5, 4, 1, 2, 3], '最大值与次大值同处左半区'),
             ([1, 2, 3, 4, 5], '最大值与次大值同处右半区')]
    for n in (3, 7, 8, 9, 31, 32, 33, 99999, 100000):
        a = list(range(1, n + 1))
        cases.append((a[:], f'n={n} 递增'))
        cases.append((a[::-1], f'n={n} 递减'))
        rng.shuffle(a)
        cases.append((a, f'n={n} 固定种子乱序'))
    for first, second in ((49999, 50000), (50000, 49999), (0, 99999), (99999, 0)):
        a = list(range(1, 100001))
        a[first], a[-1] = a[-1], a[first]
        pos = a.index(99999)
        a[second], a[pos] = a[pos], a[second]
        cases.append((a, f'最大值与次大值在位置 {first + 1}、{second + 1}'))
    data = ROOT / 'local_data'
    data.mkdir(exist_ok=True)
    oj_data = ROOT / 'data'
    oj_data.mkdir(exist_ok=True)
    (oj_data / 'compare.cpp').write_bytes((ROOT / 'compare_interactive.cpp').read_bytes())
    manifest = []
    for idx, (a, purpose) in enumerate(cases, 1):
        n = len(a)
        assert 2 <= n <= 100000 and sorted(a) == list(range(1, n + 1))
        stem = f'{idx:02d}'
        # Only n is public. The permutation is private judge data in .ans.
        (data / f'{stem}.in').write_bytes(f'{n}\n'.encode())
        (data / f'{stem}.ans').write_bytes((' '.join(map(str, a)) + '\n').encode())
        x, letters = idx, ''
        while x:
            x, rem = divmod(x - 1, 26)
            letters = chr(97 + rem) + letters
        oj_stem = 'case' + letters
        (oj_data / f'{oj_stem}.in').write_bytes(b'0\n')
        (oj_data / f'{oj_stem}.ans').write_bytes((str(n) + '\n' + ' '.join(map(str, a)) + '\n').encode())
        manifest.append({'id': stem, 'oj_id': oj_stem, 'n': n, 'maximum_index': a.index(n) + 1, 'purpose': purpose})
    (ROOT / 'data_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'Generated {len(cases)} cases.')


if __name__ == '__main__':
    main()
