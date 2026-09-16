"""Local two-process interactive runner for trusted test programs (POSIX)."""
from pathlib import Path
import argparse
import json
import os
import shutil
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def build(dest, sanitize=False):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for name in ('makefile', 'judge.h', 'compare.c', 'interactor.c'):
        shutil.copyfile(ROOT / 'local_data' / name, dest / name)
    cmd = ['make', '-B']
    if sanitize:
        cmd.append('CFLAGS=-std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer')
    subprocess.run(cmd, cwd=dest, check=True, capture_output=True, timeout=30)
    flags = ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-pedantic']
    if sanitize:
        flags += ['-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run(['cc', *flags, str(ROOT / 'answer.c'), '-o', str(dest / 'answer')],
                   check=True, capture_output=True, timeout=30)


def interact(build_dir, input_path, answer_path, solution, work, timeout=3):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    paths = {k: work / k for k in ('report', 'program.out', 'trace.txt', 'solution.err', 'judge.err')}
    # Each call owns fresh files, including when a previous run timed out.
    for path in paths.values():
        path.write_bytes(b'')
    s_read, j_write = os.pipe()
    j_read, s_write = os.pipe()
    processes = []
    expired = False
    try:
        with paths['solution.err'].open('wb') as se, paths['judge.err'].open('wb') as je:
            judge = subprocess.Popen(
                [str(Path(build_dir) / 'interactor'), str(input_path), str(answer_path),
                 str(paths['report']), str(paths['program.out']), str(paths['trace.txt'])],
                stdin=j_read, stdout=j_write, stderr=je, close_fds=True, start_new_session=True)
            processes.append(judge)
            contestant = subprocess.Popen(solution, stdin=s_read, stdout=s_write, stderr=se,
                                          close_fds=True, start_new_session=True)
            processes.append(contestant)
        for fd in (s_read, j_write, j_read, s_write):
            os.close(fd)
        s_read = j_write = j_read = s_write = -1
        deadline = time.monotonic() + timeout
        while any(p.poll() is None for p in processes):
            if time.monotonic() >= deadline:
                expired = True
                break
            time.sleep(0.002)
    finally:
        for fd in (s_read, j_write, j_read, s_write):
            if fd != -1:
                os.close(fd)
        for process in processes:
            # Also clean up descendants if the group leader has already exited.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for process in processes:
            process.wait(timeout=2)

    report = paths['report'].read_text(errors='replace').splitlines()
    score = report[0] if report else '0'
    reason = report[1] if len(report) > 1 else 'No interactor verdict'
    accepted = not expired and score == '1' and all(p.returncode == 0 for p in processes)
    if expired:
        reason = 'Interaction timeout (possibly missing flush or waiting after final answer)'
    elif contestant.returncode != 0:
        reason = f'Contestant exited with {contestant.returncode}; {reason}'
    if accepted:
        checked = subprocess.run([str(Path(build_dir) / 'compare'), str(input_path), str(answer_path),
                                  str(paths['program.out'])], check=True, capture_output=True, timeout=3)
        accepted = checked.stdout.startswith(b'1\n')
        if not accepted:
            reason = 'Post-interaction checker rejected transcript'
    return {'accepted': accepted, 'timeout': expired, 'reason': reason,
            'solution_exit': contestant.returncode, 'interactor_exit': judge.returncode,
            'trace': paths['trace.txt'].read_text(errors='replace'),
            'solution_stderr': paths['solution.err'].read_text(errors='replace'),
            'judge_stderr': paths['judge.err'].read_text(errors='replace')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', default='01', help='data file stem')
    parser.add_argument('--timeout', type=float, default=3)
    parser.add_argument('--log', type=Path)
    parser.add_argument('solution', nargs=argparse.REMAINDER, help='optional -- /path/to/program [args]')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='buaa-interactive-') as tmp:
        work = Path(tmp)
        build(work / 'bin')
        solution = args.solution
        if solution[:1] == ['--']:
            solution = solution[1:]
        result = interact(work / 'bin', ROOT / 'local_data' / f'{args.case}.in',
                          ROOT / 'local_data' / f'{args.case}.ans', solution or [str(work / 'bin' / 'answer')],
                          work / 'run', args.timeout)
        if args.log:
            args.log.write_text(result['trace'])
        print(result['trace'], end='')
        print(json.dumps({k: v for k, v in result.items() if k != 'trace'}, ensure_ascii=False, indent=2))
        return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
