#ifndef JUDGE_H
#define JUDGE_H
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

#define MAX_N 100000
#define QUERY_LIMIT 40
static int a[MAX_N + 1], used[MAX_N + 1], n;

static int integer(FILE *f, int limit, int *out) {
    int c, v = 0, len = 0;
    do { c = fgetc(f); } while (c != EOF && isspace((unsigned char)c));
    if (c < '0' || c > '9') return 0;
    do {
        int d = c - '0';
        if (++len > 8 || v > limit / 10 || (v == limit / 10 && d > limit % 10)) return 0;
        v = v * 10 + d;
        c = fgetc(f);
    } while (c >= '0' && c <= '9');
    if (c != EOF && !isspace((unsigned char)c)) return 0;
    *out = v;
    return 1;
}

static int end(FILE *f) {
    int c;
    while ((c = fgetc(f)) != EOF) {
        if (!isspace((unsigned char)c)) return 0;
    }
    return !ferror(f);
}

static int load_data(const char *public_path, const char *secret_path) {
    FILE *f = fopen(public_path, "rb");
    if (!f) return 0;
    int ok = integer(f, MAX_N, &n) && n >= 2 && end(f);
    fclose(f);
    if (!ok) return 0;
    f = fopen(secret_path, "rb");
    if (!f) return 0;
    for (int i = 1; i <= n; i++) {
        if (!integer(f, n, &a[i]) || a[i] < 1 || used[a[i]]) {
            fclose(f);
            return 0;
        }
        used[a[i]] = 1;
    }
    ok = end(f);
    fclose(f);
    return ok;
}

/* Lines are bounded and must end in a newline, as specified in the protocol. */
static int line(FILE *f, char *s, int cap) {
    int c, len = 0;
    while ((c = fgetc(f)) != EOF) {
        if (c == '\n') {
            s[len] = '\0';
            return 1;
        }
        if (c == 0 || len >= cap - 1) return -1;
        s[len++] = (char)c;
    }
    return len == 0 && !ferror(f) ? 0 : -1;
}

static int field(const char **p, int *out) {
    while (**p && isspace((unsigned char)**p)) (*p)++;
    if (**p < '0' || **p > '9') return 0;
    int v = 0, len = 0;
    while (**p >= '0' && **p <= '9') {
        int d = *(*p)++ - '0';
        if (++len > 6 || v > MAX_N / 10 || (v == MAX_N / 10 && d > MAX_N % 10)) return 0;
        v = v * 10 + d;
    }
    if (**p && !isspace((unsigned char)**p)) return 0;
    *out = v;
    return 1;
}

static int command(const char *s, char *op, int *l, int *r) {
    while (*s && isspace((unsigned char)*s)) s++;
    *op = *s++;
    if (*op != '?' && *op != '!') return 0;
    if (!*s || !isspace((unsigned char)*s)) return 0;
    if (!field(&s, l)) return 0;
    if (*op == '?' && !field(&s, r)) return 0;
    while (*s && isspace((unsigned char)*s)) s++;
    return *s == '\0';
}

static int second_max(int l, int r) {
    int first = 0, second = 0;
    for (int i = l; i <= r; i++) {
        if (a[i] > a[first]) {
            second = first;
            first = i;
        } else if (a[i] > a[second]) {
            second = i;
        }
    }
    return second;
}
#endif
