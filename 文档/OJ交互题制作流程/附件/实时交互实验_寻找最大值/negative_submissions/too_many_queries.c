#include <stdio.h>
int main(void) {
    int n, s;
    if (scanf("%d", &n) != 1 || n == 0) return 0;
    for (int i = 0; i < 41; i++) {
        puts("? 1 2");
        fflush(stdout);
        if (scanf("%d", &s) != 1 || s == -1) return 0;
    }
    return 0;
}
