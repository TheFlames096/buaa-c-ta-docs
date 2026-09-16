// BUAA experimental interactive adapter. Compile as C++14.
// Reuses /utils/process_monitor; never executes a submission as root directly.
#include <algorithm>
#include <cerrno>
#include <chrono>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

using namespace std;
using Clock = chrono::steady_clock;

static int verdict(bool ok, const string &reason) {
    printf("%d\n%s\n", ok ? 1 : 0, ok ? "Accepted" : "Wrong Answer");
#ifdef SPJ_DIAGNOSTIC
    if (!ok) printf("%s\n", reason.c_str());
#else
    (void)reason;
#endif
    return 0;
}

static bool send_line(int fd, int value) {
    string s = to_string(value) + "\n";
    return write(fd, s.data(), s.size()) == (ssize_t)s.size();
}

static string read_text(const string &path) {
    ifstream f(path);
    string s, line;
    while (s.size() < 4096 && getline(f, line)) s += line + "\n";
    return s;
}

static bool monitor_ok(const string &report) {
    istringstream f(report);
    string line;
    bool run_ok = false, exit_ok = false;
    while (getline(f, line)) {
        auto colon = line.find(':');
        if (colon == string::npos) continue;
        string key = line.substr(0, colon), value = line.substr(colon + 1);
        transform(key.begin(), key.end(), key.begin(), [](unsigned char c) { return tolower(c); });
        key.erase(key.find_last_not_of(" \t\r") + 1);
        value.erase(0, value.find_first_not_of(" \t\r"));
        value.erase(value.find_last_not_of(" \t\r") + 1);
        if (key == "run result code") run_ok = value == "0";
        if (key == "exit code") exit_ok = value == "0";
    }
    return run_ok && exit_ok;
}

int main(int argc, char **argv) {
    signal(SIGPIPE, SIG_IGN);
    if (argc != 4) return verdict(false, "judge requires three file paths");
    if (access("/utils/process_monitor", X_OK) || access("/test/main", X_OK)) {
        return verdict(false, "required BUAA execution interface is unavailable");
    }
    // Public file is a preflight sentinel; the private file contains n and permutation.
    ifstream public_file(argv[1]), private_file(argv[2]);
    int sentinel, n;
    string extra;
    if (!(public_file >> sentinel) || sentinel != 0 || (public_file >> extra) ||
        !(private_file >> n) || n < 2 || n > 100000) return verdict(false, "invalid judge data");
    vector<int> a(n + 1), used(n + 1);
    for (int i = 1; i <= n; i++) {
        if (!(private_file >> a[i]) || a[i] < 1 || a[i] > n || used[a[i]]++) {
            return verdict(false, "private data is not a permutation");
        }
    }
    if (private_file >> extra) return verdict(false, "extra private data");
    public_file.close();
    private_file.close();

    char directory[] = "/test/spjinteractiveXXXXXX";
    if (!mkdtemp(directory)) return verdict(false, "cannot create private communication directory");
    string dir = directory, in_path = dir + "/input", out_path = dir + "/output";
    string report_path = dir + "/monitor", error_path = dir + "/stderr";
    auto cleanup = [&]() {
        unlink(in_path.c_str()); unlink(out_path.c_str());
        unlink(report_path.c_str()); unlink(error_path.c_str()); rmdir(dir.c_str());
    };
    if (mkfifo(in_path.c_str(), 0600) || mkfifo(out_path.c_str(), 0600)) {
        cleanup(); return verdict(false, "cannot create communication FIFOs");
    }
    int in_fd = open(in_path.c_str(), O_RDWR | O_NONBLOCK);
    int out_fd = open(out_path.c_str(), O_RDONLY | O_NONBLOCK);
    int report_fd = open(report_path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (in_fd < 0 || out_fd < 0 || report_fd < 0) {
        if (in_fd >= 0) close(in_fd);
        if (out_fd >= 0) close(out_fd);
        if (report_fd >= 0) close(report_fd);
        cleanup(); return verdict(false, "cannot open communication descriptors");
    }
    pid_t child = fork();
    if (child == 0) {
        setsid();
        dup2(report_fd, STDOUT_FILENO);
        dup2(report_fd, STDERR_FILENO);
        close(in_fd); close(out_fd); close(report_fd);
        // These are the same monitor, uid/gid and redirection options used by judge.py.
        // Only native C/C++ executables are supported by this adapter.
        execl("/utils/process_monitor", "process_monitor", "-t", "1000", "-m", "65536",
              "-p", "5", "-uid", "8194", "-gid", "8194", "-inf", in_path.c_str(),
              "-outf", out_path.c_str(), "-errf", error_path.c_str(), "/test/main", (char *)NULL);
        _exit(127);
    }
    close(report_fd);
    if (child < 0) {
        close(in_fd); close(out_fd); cleanup(); return verdict(false, "cannot launch native monitor");
    }

    auto deadline = Clock::now() + chrono::seconds(3);
    bool finished = false, have_answer = false, bad = false;
    int child_status = 0, queries = 0;
    string line, reason;
    if (!send_line(in_fd, n)) { bad = true; reason = "cannot send initial n"; }
    while (!bad && Clock::now() < deadline) {
        if (!finished && waitpid(child, &child_status, WNOHANG) == child) finished = true;
        char buffer[512];
        ssize_t len = read(out_fd, buffer, sizeof(buffer));
        if (len < 0 && errno != EAGAIN && errno != EINTR) {
            bad = true; reason = "cannot read contestant output"; break;
        }
        if (len > 0) {
            for (ssize_t i = 0; i < len && !bad; i++) {
                unsigned char c = buffer[i];
                if (have_answer) {
                    if (!isspace(c)) { bad = true; reason = "extra output after final answer"; }
                    continue;
                }
                if (c != '\n') {
                    if (c == 0 || line.size() >= 127) { bad = true; reason = "invalid or oversized command"; }
                    else line += (char)c;
                    continue;
                }
                istringstream cmd(line);
                string op, tail;
                int l, r;
                if (!(cmd >> op >> l)) { bad = true; reason = "invalid command"; }
                else if (op == "?") {
                    if (!(cmd >> r) || (cmd >> tail) || l < 1 || l >= r || r > n) {
                        bad = true; reason = "invalid query range or format";
                    } else if (++queries > 40) { bad = true; reason = "more than 40 queries"; }
                    else {
                        int first = 0, second = 0;
                        for (int j = l; j <= r; j++) {
                            if (a[j] > a[first]) { second = first; first = j; }
                            else if (a[j] > a[second]) second = j;
                        }
                        if (!send_line(in_fd, second)) { bad = true; reason = "contestant stopped reading"; }
                    }
                } else if (op == "!") {
                    if ((cmd >> tail) || l < 1 || l > n || a[l] != n) {
                        bad = true; reason = "wrong maximum position";
                    } else have_answer = true;
                } else { bad = true; reason = "unknown command"; }
                line.clear();
            }
        } else if (finished) break;
        else {
            struct pollfd p = {out_fd, POLLIN, 0};
            poll(&p, 1, 5);
        }
    }
    if (!finished && !bad) { bad = true; reason = "interaction wall time limit exceeded"; }
    if (bad) (void)send_line(in_fd, -1);
    close(in_fd);
    close(out_fd);
    if (!finished) {
        // Allow the platform monitor to terminate and reap its sandboxed process.
        auto grace = Clock::now() + chrono::milliseconds(1500);
        while (Clock::now() < grace) {
            if (waitpid(child, &child_status, WNOHANG) == child) { finished = true; break; }
            usleep(5000);
        }
        if (!finished) {
            kill(-child, SIGKILL);
            kill(child, SIGKILL);
            waitpid(child, &child_status, 0);
        }
    }
    string report = read_text(report_path);
    string errors = read_text(error_path);
    bool ok = !bad && have_answer && line.empty() && WIFEXITED(child_status) &&
              WEXITSTATUS(child_status) == 0 && monitor_ok(report);
    if (!ok && reason.empty()) reason = have_answer ? "native monitor rejected execution" : "missing final answer";
    // Diagnostics are bounded and only concern this run. No private array is printed.
    if (!ok && !report.empty()) reason += "; monitor: " + report.substr(0, 900);
    if (!ok && !errors.empty()) reason += "; stderr: " + errors.substr(0, 200);
    cleanup();
    return verdict(ok, reason);
}
