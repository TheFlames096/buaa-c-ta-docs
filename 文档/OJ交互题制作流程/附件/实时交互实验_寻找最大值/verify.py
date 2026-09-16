from pathlib import Path
import itertools
import json
import random
import subprocess
import sys
import tempfile

from run_local import ROOT, build, interact


def main():
    stats = {'data_cases': 0, 'live_small_permutations': 0, 'independent_reply_checks': 0,
             'protocol_rejections': 0, 'sanitizer_cases': 0, 'maximum_queries_observed': 0}
    rng = random.Random(20260914)
    with tempfile.TemporaryDirectory(prefix='verify-interaction-') as tmp:
        work = Path(tmp)
        binaries = work / 'bin'
        build(binaries)
        public, secret = work / 'test.in', work / 'test.ans'

        def data(a):
            public.write_text(f'{len(a)}\n')
            secret.write_text(' '.join(map(str, a)) + '\n')

        def check(a, binary_dir=binaries):
            data(a)
            result = interact(binary_dir, public, secret, [str(binary_dir / 'answer')], work / 'run')
            assert result['accepted'], result
            assert not result['judge_stderr'] and not result['solution_stderr'], result
            trace = result['trace'].splitlines()
            queries = 0
            for i, line in enumerate(trace):
                if line.startswith('S> ? '):
                    _, _, l, r = line.split()
                    l, r = int(l), int(r)
                    expected = sorted(range(l, r + 1), key=lambda j: a[j - 1], reverse=True)[1]
                    assert trace[i + 1] == f'J> {expected}', (a, trace)
                    queries += 1
                    stats['independent_reply_checks'] += 1
                if line.startswith('S> ! '):
                    assert int(line.split()[-1]) == a.index(len(a)) + 1
            assert queries <= 40
            stats['maximum_queries_observed'] = max(stats['maximum_queries_observed'], queries)
            return result

        manifest = json.loads((ROOT / 'data_manifest.json').read_text())
        for case in manifest:
            src = ROOT / 'local_data' / case['id']
            assert src.with_suffix('.in').read_bytes() == f"{case['n']}\n".encode()
            raw = src.with_suffix('.ans').read_bytes()
            assert b'\r' not in raw
            a = list(map(int, raw.split()))
            assert sorted(a) == list(range(1, len(a) + 1))
            assert case['maximum_index'] == a.index(len(a)) + 1
            check(a)
            stats['data_cases'] += 1
        for n in range(2, 7):
            for a in itertools.permutations(range(1, n + 1)):
                check(list(a))
                stats['live_small_permutations'] += 1
        for n in (1000, 10000, 100000):
            for _ in range(3):
                a = list(range(1, n + 1))
                rng.shuffle(a)
                check(a)

        # Protocol failures are tested against the real two-process connection.
        mock = work / 'mock.py'
        bad = ["print('? 0 2', flush=True)", "print('? 1 1', flush=True)",
               "print('? 1 3', flush=True)", "print('! 2', flush=True)",
               "print('! 0', flush=True)", "print('! 3', flush=True)",
               "print('! 1 extra', flush=True)", "print('! 1\\nextra', flush=True)",
               "print('? 1 999999999999999999', flush=True)",
               "print('X' * 1000, flush=True)", "print('? 1 2 extra', flush=True)",
               "print('? 1 2\\x00', flush=True)", "print('', flush=True)",
               "sys.stdout.write('! 1'); sys.stdout.flush()", "pass",
               "for i in range(41):\n print('? 1 2', flush=True)\n sys.stdin.readline()"]
        data([2, 1])
        for body in bad:
            mock.write_text('import sys\nsys.stdin.readline()\n' + body + '\n')
            result = interact(binaries, public, secret, [sys.executable, str(mock)], work / 'bad', timeout=2)
            assert not result['accepted'] and not result['timeout'], (body, result)
            stats['protocol_rejections'] += 1
        for body in ("sys.stdout.write('? 1 2\\n'); sys.stdin.readline()",
                     "print('! 1', flush=True); sys.stdin.readline()"):
            mock.write_text('import sys\nsys.stdin.readline()\n' + body + '\n')
            result = interact(binaries, public, secret, [sys.executable, str(mock)], work / 'bad', timeout=0.4)
            assert not result['accepted'] and result['timeout'], result
            stats['protocol_rejections'] += 1

        # A contestant crash must not become AC even after a correct final answer.
        mock.write_text("import sys\nsys.stdin.readline()\nprint('! 1', flush=True)\nsys.exit(7)\n")
        result = interact(binaries, public, secret, [sys.executable, str(mock)], work / 'bad')
        assert not result['accepted'] and result['solution_exit'] == 7
        stats['protocol_rejections'] += 1

        # Same solution in the documented ordinary file pipeline gets no reply.
        probe = work / 'probe'
        probe_compare = work / 'probe_compare'
        for source, binary in (('oj_probe.c', probe), ('oj_probe_compare.c', probe_compare)):
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', str(ROOT / source), '-o', str(binary)], check=True)
        output = subprocess.run([str(probe)], input=b'2\n', capture_output=True, check=True).stdout
        assert output == b'? 1 2\nNO_REPLY_EOF\n'
        (work / 'probe.out').write_bytes(output)
        v = subprocess.run([str(probe_compare), str(public), str(secret), str(work / 'probe.out')],
                           capture_output=True, check=True).stdout
        assert v.startswith(b'0\nNO_LIVE_REPLY:')
        stats['ordinary_pipeline_probe'] = v.decode().strip()

        # Address/undefined behavior instrumentation on both sides and checker.
        san = work / 'san'
        build(san, sanitize=True)
        for a in ([2, 1], [1, 2], [2, 5, 1, 4, 3], list(range(1, 100001))):
            check(a, san)
            stats['sanitizer_cases'] += 1

        problem = (ROOT / 'problem.md').read_text()
        assert '```' not in problem
        solution = (ROOT / 'solution.md').read_text().split('```c\n')[1].split('```')[0]
        assert solution == (ROOT / 'answer.c').read_text()
        for idx, a in ((1, [2, 1]), (2, [2, 5, 1, 4, 3])):
            result = check(a)
            for kind, prefix in (('输入', 'J> '), ('输出', 'S> ')):
                section = problem.split(f'## {kind}样例 ({idx})\n', 1)[1].split('\n## ', 1)[0]
                sample = [line[4:] for line in section.splitlines() if line.startswith('    ')]
                assert sample == [line[3:] for line in result['trace'].splitlines() if line.startswith(prefix)]

    (ROOT / 'verification.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
