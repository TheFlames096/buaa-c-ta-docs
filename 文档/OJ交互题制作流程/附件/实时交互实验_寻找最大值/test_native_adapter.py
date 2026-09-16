"""Run only in a disposable Linux container.

The mock reproduces process_monitor's flags/report for transport tests.
It does not establish compatibility with the actual BUAA monitor; live OJ
submissions are the evidence for that part.
"""
from pathlib import Path
import json
import subprocess

ROOT = Path('/work')
MOCK = r'''#!/usr/bin/python3
import os, resource, subprocess, sys
args=sys.argv[1:]
options={}
while args and args[0].startswith('-'):
    key=args.pop(0)
    options[key]=args.pop(0)
def restrict():
    os.setgroups([])
    os.setgid(int(options['-gid']))
    os.setuid(int(options['-uid']))
    resource.setrlimit(resource.RLIMIT_CPU,(1,1))
    resource.setrlimit(resource.RLIMIT_AS,(64*1024**2,64*1024**2))
with open(options['-inf'],'rb',buffering=0) as inf, open(options['-outf'],'wb',buffering=0) as outf, open(options['-errf'],'wb',buffering=0) as errf:
    child=subprocess.Popen(args,stdin=inf,stdout=outf,stderr=errf,preexec_fn=restrict)
    try:
        status=child.wait(timeout=1)
        result=0 if status==0 else 1
    except subprocess.TimeoutExpired:
        child.kill();child.wait();status=-9;result=2
print('Run result: mock monitor')
print('Run result code: '+str(result))
print('Exit code: '+str(status))
print('Time used: 0')
print('Mem used: 0')
'''


def main():
    Path('/test').mkdir(exist_ok=True)
    Path('/utils').mkdir(exist_ok=True)
    Path('/data').mkdir(exist_ok=True, mode=0o700)
    monitor = Path('/utils/process_monitor')
    assert not monitor.exists(), 'This is only for a disposable test container.'
    monitor.write_text(MOCK)
    monitor.chmod(0o755)
    subprocess.run(['g++', '-O2', '-std=c++14', '-Wall', '-Wextra', '-Werror',
                    str(ROOT / 'compare_interactive.cpp'), '-o', '/test/compare'], check=True)
    Path('/data/input').write_text('0\n')
    Path('/data/output').write_text('')

    def compile_source(source):
        Path('/test/main.c').write_text(source)
        subprocess.run(['gcc', '-O2', '-std=c99', '/test/main.c', '-o', '/test/main'], check=True)

    def check(a, expected):
        Path('/data/answer').write_text(str(len(a)) + '\n' + ' '.join(map(str, a)) + '\n')
        result = subprocess.run(['/test/compare', '/data/input', '/data/answer', '/data/output'],
                                cwd='/test', capture_output=True, timeout=6, check=True)
        assert result.stdout.splitlines()[0] == str(expected).encode(), result.stdout.decode()
        assert not list(Path('/test').glob('spjinteractive*')), 'run left temporary communication files'
        return result.stdout.decode()

    compile_source((ROOT / 'answer.c').read_text())
    manifest = json.loads((ROOT / 'data_manifest.json').read_text())
    for case in manifest:
        a = list(map(int, (ROOT / 'local_data' / (case['id'] + '.ans')).read_text().split()))
        check(a, 1)
    boot = subprocess.run(['/test/main'], input=b'0\n', capture_output=True, check=True)
    assert boot.stdout == b''
    mutations = [
        'puts("! 2");',
        'puts("? 0 2");',
        'puts("? 1 1");',
        'puts("! 1 junk");',
        'puts("! 1\\nextra");',
        'for(int i=0;i<41;i++){puts("? 1 2");fflush(stdout);scanf("%d",&n);}',
        'puts("? 1 2");scanf("%d",&n);',  # no flush
        'puts("! 1");fflush(stdout);return 7;',
        'fputs("! 1",stdout);',  # missing newline
        'for(int i=0;i<1000;i++)putchar(65);',
        'puts("! 1");fflush(stdout);for(;;){}',
    ]
    for body in mutations:
        compile_source('#include <stdio.h>\nint main(void){int n;if(scanf("%d",&n)!=1||n==0)return 0;' + body + 'return 0;}')
        check([2, 1], 0)
    compile_source('#include <stdio.h>\nint main(void){int n;if(scanf("%d",&n)!=1||n==0)return 0;puts("! 1");return 0;}')
    check([2, 1], 1)
    print(json.dumps({'transport_cases': len(manifest), 'protocol_failures': len(mutations),
                      'zero_query_valid_answer': 1, 'preflight_exit': 'passed',
                      'monitor': 'local mock; native compatibility requires OJ tests'}))


if __name__ == '__main__':
    main()
