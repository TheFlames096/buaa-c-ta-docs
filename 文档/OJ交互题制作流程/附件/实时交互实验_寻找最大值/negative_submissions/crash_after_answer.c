#include <stdio.h>
#include <stdlib.h>

int ask(int l, int r) {
    if (l == r) return 0;
    printf("? %d %d\n", l, r);
    fflush(stdout);
    int s;
    if (scanf("%d", &s) != 1) exit(0);
    if (s == -1) exit(0);
    return s;
}

int main(void) {
    int n;
    if (scanf("%d", &n) != 1 || n == 0) return 0;
    int l = 1, r = n;
    while (l < r) {
        int s = ask(l, r);
        int mid = (l + r) / 2;
        if (s <= mid) {
            if (ask(l, mid) == s) {
                r = mid;
            } else {
                l = mid + 1;
            }
        } else {
            if (ask(mid + 1, r) == s) {
                l = mid + 1;
            } else {
                r = mid;
            }
        }
    }
    printf("! %d\n", l);
    fflush(stdout);
    return 7;
}
