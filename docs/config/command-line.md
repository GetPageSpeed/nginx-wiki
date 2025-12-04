---
title: Command-line & process management
description: This tutorial shows you how to start, stop, and control NGINX from the command line.
---

# Command-line & process management

NGINX exposes a small command-line interface that controls the **master process**. This page shows you how to start NGINX, and once it's running, how to control it so that it will stop or restart.

## Starting NGINX

NGINX is invoked from the command line, usually from `/usr/bin/nginx` or `/usr/local/nginx/sbin/nginx`.

### Basic Example

```bash
/usr/bin/nginx
```

### Advanced Example

```bash
/usr/bin/nginx -t -c ~/mynginx.conf -g "pid /var/run/nginx.pid; worker_processes 2;"
```

## Command-line Options

| Option | Description |
|--------|-------------|
| `-?, -h` | Print help |
| `-v` | Print version |
| `-V` | Print NGINX version, compiler version and configure parameters |
| `-t` | Test configuration file syntax and try to open files referred in configuration |
| `-T` | Same as `-t`, but also dump configuration |
| `-q` | Suppress non-error messages during configuration testing |
| `-s signal` | Send signal to master process: `stop`, `quit`, `reopen`, `reload` |
| `-p prefix` | Set prefix path (default: `/usr/local/nginx/`) |
| `-c filename` | Specify which configuration file NGINX should use instead of the default |
| `-g directives` | Set global directives |

!!! note
    NGINX has only a few command-line parameters. Unlike many other software systems, the configuration is done entirely via the configuration file.

---

## Stopping or Restarting NGINX

There are two ways to control NGINX once it's already running.

### Method 1: Using `-s` flag

```bash
/usr/bin/nginx -s stop    # Fast shutdown
/usr/bin/nginx -s quit    # Graceful shutdown
/usr/bin/nginx -s reload  # Reload configuration
/usr/bin/nginx -s reopen  # Reopen log files
```

### Method 2: Sending Signals

By default NGINX writes its master process id to `/usr/local/nginx/logs/nginx.pid`. You can send signals directly to the master process:

```bash
kill -QUIT $( cat /usr/local/nginx/logs/nginx.pid )
```

## Master Process Signals

| Signal | Description |
|--------|-------------|
| `TERM`, `INT` | Quick shutdown |
| `QUIT` | Graceful shutdown |
| `KILL` | Halts a stubborn process |
| `HUP` | Reload configuration, start new workers with new config, gracefully shutdown old workers |
| `USR1` | Reopen the log files |
| `USR2` | Upgrade executable on the fly |
| `WINCH` | Gracefully shutdown the worker processes |

## Worker Process Signals

There's no need to control the worker processes yourself. However, they support some signals too:

| Signal | Description |
|--------|-------------|
| `TERM`, `INT` | Quick shutdown |
| `QUIT` | Graceful shutdown |
| `USR1` | Reopen the log files |

---

## Loading a New Configuration Using Signals

When NGINX receives the `HUP` signal, it tries to parse the configuration file (the specified one, if present, otherwise the default), and if successful, tries to apply a new configuration (i.e. re-open the log files and listen sockets).

If successful, NGINX runs new worker processes and signals graceful shutdown to old workers. Notified workers close listen sockets but continue to serve current clients. After serving all clients old workers shutdown.

If NGINX couldn't successfully apply the new configuration, it continues to work with the old configuration.

---

## Upgrading the Binary On The Fly

If you need to replace NGINX binary with a new one (when upgrading to a new version or adding/removing modules), you can do it without any service downtime—no incoming requests will be lost.

1. Replace old binary with a new one
2. Send `USR2` signal to the master process:

```bash
kill -USR2 $( cat /usr/local/nginx/logs/nginx.pid )
```

The master process renames its `.pid` file to `.oldbin`, then executes a new binary, which starts a new master process and new worker processes.

3. At this point, two instances of NGINX are running, handling requests together.

4. Send `WINCH` signal to the old master process to gracefully shut down its workers:

```bash
kill -WINCH $( cat /usr/local/nginx/logs/nginx.pid.oldbin )
```

5. After old workers quit, send `QUIT` to the old master:

```bash
kill -QUIT $( cat /usr/local/nginx/logs/nginx.pid.oldbin )
```

### Rolling Back

If something goes wrong, you can revert to the old server:

1. Send `HUP` to the old master process (starts worker processes without reloading config)
2. Send `QUIT` to the new master process to gracefully shut down its workers
3. Send `TERM` to the new master process to force it to quit

