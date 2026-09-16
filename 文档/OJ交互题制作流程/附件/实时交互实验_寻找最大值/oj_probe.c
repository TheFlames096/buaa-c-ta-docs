#include <stdio.h>

int main(void) {
    int n, reply;
    if (scanf("%d", &n) != 1) return 0;
    printf("? 1 %d\n", n);
    fflush(stdout);
    if (scanf("%d", &reply) != 1) {
        puts("NO_REPLY_EOF");
        return 0;
    }
    printf("RECEIVED_REPLY %d\n", reply);
    return 0;
}
