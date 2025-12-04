---
title: Debugging
description: This tutorial explains how to use some of NGINX's essential debugging features.
---

# Debugging

NGINX has a wide range of debugging features, including detailed debug logging. Understanding NGINX internals often starts with **debug builds and verbose logging**.

!!! note
    Most debugging features are only activated when NGINX is compiled with `--with-debug` configure argument.

---

## Debugging Log

To activate debugging log you have to:

1. Compile NGINX with `--with-debug` configure option
2. Set debug level in `error_log` directive

```nginx
error_log /var/log/nginx/error.log debug;
```

It's possible to debug only connections from specified addresses via `debug_connection` directive:

```nginx
events {
    debug_connection 192.168.1.1;
    debug_connection 192.168.10.0/24;
}
```

!!! tip
    In hard cases (e.g. debugging event method related problems) it's a good idea to obtain full debugging log by setting debug level in global `error_log`.

---

## Core Dump

To obtain core dumps you usually have to tune your OS. Though NGINX simplifies some typical cases and usually adding:

```nginx
worker_rlimit_core  500M;
working_directory   /path/to/cores/;
```

to nginx.conf is enough.

Then run gdb to obtain backtrace:

```bash
gdb /path/to/nginx /path/to/cores/nginx.core
backtrace full
```

### Building with Debug Symbols

If your gdb backtrace warns that "No symbol table info available" then you will need to recompile NGINX with the appropriate compiler flags for debugging symbols.

The exact flags required depend on the compiler used. If you use GCC, the flag `-g` enables the inclusion of debugging symbols. Additionally disabling compiler optimization using `-O0` will make the debugger output easier to understand.

```bash
CFLAGS="-g -O0" ./configure --with-debug
make
sudo make install
```

---

## Socket Leaks

Sometimes socket leaks happen. This usually results in `[alert] 15248#0: open socket #123 left in connection 456` messages in error log on NGINX reload/restart/shutdown.

To debug, add:

```nginx
debug_points abort;
```

to `nginx.conf` and configure core dumps (see above). This will result in `abort()` call once NGINX detects leak and core dump.

Something like this in gdb should be useful (assuming 456 is connection number from error message):

```bash
set $c = &ngx_cycle->connections[456]
p $c->log->connection
p *$c
set $r = (ngx_http_request_t *) $c->data
p *$r
```

In particular, `p $c->log->connection` will print connection number as used in logs. It will be possible to grep debug log for relevant lines:

```bash
fgrep ' *12345678 ' /path/to/error_log
```

---

## Asking for Help

When asking for help with debugging please provide:

- `nginx -V` output
- Full config
- Debug log
- Backtrace (if NGINX exits on signal)

