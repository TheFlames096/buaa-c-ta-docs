#include "judge.h"

static int verdict(int ok, const char *message) {
    printf("%d\n%s\n", ok, message);
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 4) return verdict(0, "Judge error: expected input, answer, contestant output");
    if (!load_data(argv[1], argv[2])) return verdict(0, "Judge error: invalid data");
    FILE *f = fopen(argv[3], "rb");
    if (!f) return verdict(0, "Judge error: cannot open contestant output");
    char buf[128], op;
    int l, r = 0, queries = 0;
    while (line(f, buf, sizeof(buf)) == 1) {
        if (!command(buf, &op, &l, &r)) break;
        if (op == '?') {
            if (l < 1 || l >= r || r > n || ++queries > QUERY_LIMIT) break;
            /* Replay can compute replies, but cannot send them to an ended process. */
            (void)second_max(l, r);
        } else {
            int ok = l >= 1 && l <= n && a[l] == n && end(f);
            fclose(f);
            return verdict(ok, ok ? "Accepted final answer and query format" : "Wrong final answer or extra output");
        }
    }
    fclose(f);
    return verdict(0, "Invalid transcript or missing final answer");
}
