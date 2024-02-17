#define _GNU_SOURCE

#include <seccomp.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/random.h>
#include <sys/stat.h> 
#include <dirent.h>

void seccomp()
{
    scmp_filter_ctx ctx;
    ctx = seccomp_init(SCMP_ACT_KILL);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_read, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_write, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_exit_group, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_execve, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_brk, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_access, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_openat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_fstat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_mmap, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_close, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_arch_prctl, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_mprotect, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_munmap, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_set_tid_address, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_set_robust_list, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_rt_sigaction, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_rt_sigprocmask, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_prlimit64, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_futex, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_sysinfo, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_poll, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_umask, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_chmod, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_sigaltstack, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_sched_setaffinity, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_sched_getaffinity, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_getcwd, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_readlink, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_statx, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_getrandom, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_getrusage, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_uname, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_lstat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_getdents64, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_mremap, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_stat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_ioctl, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_getuid, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_geteuid, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_getpid, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_lseek, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_pipe2, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_clone, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_dup2, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_dup, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_wait4, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_pread64, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_madvise, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_open, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_prctl, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_fcntl, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_statfs, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_flock, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_socketpair, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_mkdir, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_unlink, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_chdir, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_rename, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_unlinkat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_tgkill, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_sched_yield, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_exit, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_rt_sigreturn, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_utimensat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_linkat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_vfork, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_newfstatat, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_rseq, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_clone3, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_close_range, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_faccessat2, 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, __NR_ftruncate, 0);
    seccomp_load(ctx);
}

const char alphabet[] = "abcdefghijklmnopqrstuvwxyz0123456789";
char *dir_name;

void init() {
    char template[] = "/cache/YYYYYYYYYYYY.XXXXXX";
    for (size_t i = 0; i < strlen(template); ++i) {
        unsigned char c = 0;
        getrandom(&c, sizeof(c), 0);
        if (template[i] == 'Y') {
            template[i] = alphabet[c % strlen(alphabet)];
        }
    }
    dir_name = mkdtemp(strdup(template));
}

// https://stackoverflow.com/questions/2256945/removing-a-non-empty-directory-programmatically-in-c-or-c
int remove_directory(const char *path) {
   DIR *d = opendir(path);
   size_t path_len = strlen(path);
   int r = -1;

   if (d) {
      struct dirent *p;

      r = 0;
      while (!r && (p=readdir(d))) {
          int r2 = -1;
          char *buf;
          size_t len;

          /* Skip the names "." and ".." as we don't want to recurse on them. */
          if (!strcmp(p->d_name, ".") || !strcmp(p->d_name, ".."))
             continue;

          len = path_len + strlen(p->d_name) + 2; 
          buf = malloc(len);

          if (buf) {
             struct stat statbuf;

             snprintf(buf, len, "%s/%s", path, p->d_name);
             if (!stat(buf, &statbuf)) {
                if (S_ISDIR(statbuf.st_mode))
                   r2 = remove_directory(buf);
                else
                   r2 = unlink(buf);
             }
             free(buf);
          }
          r = r2;
      }
      closedir(d);
   }

   if (!r)
      r = rmdir(path);

   return r;
}

__attribute__((destructor))
void fini() {
    if (dir_name != NULL) {
        remove_directory(dir_name);
    }
}

int child(int argc, const char *argv[], char *dir_name) {
    if (argc < 2) {
        return 1;
    }

    char **new_argv = calloc(argc + 1, sizeof(*new_argv));
    for (size_t i = 0; i + 1 < argc; ++i) {
        new_argv[i] = strdup(argv[i + 1]);
    }

    new_argv[argc - 1] = dir_name;
    new_argv[argc] = NULL;

    execve(new_argv[0], new_argv, environ);

    return 1;
}

int parent(pid_t pid, char *dir_name) {
    int wstatus = 0;
    if (waitpid(pid, &wstatus, 0) == -1) {
        return 1;
    }

    if (WIFEXITED(wstatus)) {
        return WEXITSTATUS(wstatus);
    }

    return 1;
}

int main(int argc, const char *argv[]) {
    unsigned char c = 0;
    getrandom(&c, sizeof(c), 0);

    if (setgid(1337 + c) == -1) {
        return 1;
    }

    if (setuid(1337 + c) == -1) {
        return 1;
    }

    init();

    if (dir_name == NULL) {
        return 1;
    }

    pid_t pid = fork();

    if (pid < 0) {
        return 1;
    }

    if (pid == 0) {
        alarm(15);
        seccomp();
        return child(argc, argv, dir_name);
    }

    return parent(pid, dir_name);
}
