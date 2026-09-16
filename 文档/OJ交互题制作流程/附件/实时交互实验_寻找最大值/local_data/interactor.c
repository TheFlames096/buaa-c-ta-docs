#include "judge.h"
#include <signal.h>

static FILE *report, *raw, *trace;
static int queries;

static int finish(int ok, const char *message) {
    if (!ok) {
        puts("-1");
        fflush(stdout);
    }
    if (report) {
        fprintf(report, "%d\n%s; queries=%d\n", ok, message, queries);
        fclose(report);
    }
    if (raw) fclose(raw);
    if (trace) {
        fprintf(trace, "VERDICT: %s; queries=%d\n", message, queries);
        fclose(trace);
    }
    return ok ? 0 : 1;
}

int main(int argc, char **argv) {
    /* public input, private answer, report, raw contestant output, trace */
    if (argc != 6) return 2;
    signal(SIGPIPE, SIG_IGN);
    report = fopen(argv[3], "w");
    raw = fopen(argv[4], "w");
    trace = fopen(argv[5], "w");
    if (!report || !raw || !trace) return finish(0, "Judge error: cannot open logs");
    if (!load_data(argv[1], argv[2])) return finish(0, "Judge error: invalid data");
    setvbuf(trace, NULL, _IOLBF, 0);
    printf("%d\n", n);
    fflush(stdout);
    fprintf(trace, "J> %d\n", n);

    char buf[128], op;
    int l, r = 0;
    for (;;) {
        if (line(stdin, buf, sizeof(buf)) != 1) return finish(0, "Missing or malformed command");
        fprintf(raw, "%s\n", buf);
        fprintf(trace, "S> %s\n", buf);
        if (!command(buf, &op, &l, &r)) return finish(0, "Invalid command format");
        if (op == '?') {
            if (l < 1 || l >= r || r > n) return finish(0, "Invalid query range");
            if (++queries > QUERY_LIMIT) return finish(0, "Query limit exceeded");
            int s = second_max(l, r);
            printf("%d\n", s);
            if (fflush(stdout) == EOF) return finish(0, "Contestant input closed");
            fprintf(trace, "J> %d\n", s);
        } else {
            if (l < 1 || l > n || a[l] != n) return finish(0, "Wrong maximum position");
            if (!end(stdin)) return finish(0, "Extra output after final answer");
            return finish(1, "Accepted");
        }
    }
}
