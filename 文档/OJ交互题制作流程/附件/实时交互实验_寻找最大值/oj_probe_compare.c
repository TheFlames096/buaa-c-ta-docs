#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc != 4) {
        puts("0\nPROBE_BAD_ARGUMENT_COUNT");
        return 0;
    }
    FILE *f = fopen(argv[3], "rb");
    if (!f) {
        puts("0\nPROBE_OUTPUT_UNREADABLE");
        return 0;
    }
    char s[1024];
    size_t size = fread(s, 1, sizeof(s) - 1, f);
    s[size] = '\0';
    fclose(f);
    if (strstr(s, "NO_REPLY_EOF")) {
        puts("0\nNO_LIVE_REPLY: contestant read EOF after first flushed query; SPJ ran after contestant exited.");
    } else if (strstr(s, "RECEIVED_REPLY")) {
        puts("0\nREPLY_OBSERVED: inspect actual input and runner before concluding interaction support.");
    } else {
        puts("0\nPROBE_INCONCLUSIVE: no EOF or reply marker. This is an interface experiment, not a scored exercise.");
    }
    return 0;
}
