---
title: NGINX Process Model - Master-Worker Architecture Guide
description: Learn how NGINX master-worker process architecture enables high performance, graceful restarts, and fault isolation for production deployments.
keywords: nginx process model, nginx master worker, nginx architecture, nginx worker processes, nginx signals, nginx graceful reload
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - architecture
  - process model
  - master-worker
  - signals
  - shared memory
  - configuration
---

# Process Model

NGINX uses a **master/worker** architecture that provides high performance, graceful restarts, and fault isolation.

---

## Architecture Overview

```
                    ┌─────────────────┐
                    │  Master Process │
                    │    (nginx)      │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │   Worker    │   │   Worker    │   │   Worker    │
    │  Process 1  │   │  Process 2  │   │  Process N  │
    └─────────────┘   └─────────────┘   └─────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Shared Memory  │
                    │ (cache, limits) │
                    └─────────────────┘
```

---

## Master Process

The master process runs as **root** (or the user that started NGINX) and is responsible for:

### Responsibilities

1. **Reading and validating configuration**
2. **Binding to privileged ports** (80, 443)
3. **Starting, stopping, and managing workers**
4. **Handling signals** for reload, shutdown, etc.
5. **Re-opening log files**
6. **Upgrading the binary** without downtime

### Key Structure: `ngx_cycle_t`

The master maintains a global `ngx_cycle_t` structure:

```c
struct ngx_cycle_t {
    void                  ****conf_ctx;     /* Configuration contexts */
    ngx_pool_t            *pool;            /* Memory pool */
    ngx_log_t             *log;             /* Error log */
    ngx_log_t              new_log;
    ngx_connection_t      *connections;     /* Connection array */
    ngx_event_t           *read_events;     /* Read events */
    ngx_event_t           *write_events;    /* Write events */
    ngx_listening_t       *listening;       /* Listening sockets */
    ngx_array_t            paths;           /* Paths for temp files */
    ngx_array_t            config_dump;
    ngx_list_t             open_files;      /* Open files */
    ngx_list_t             shared_memory;   /* Shared memory zones */
    ngx_uint_t             connection_n;    /* Connection count */
    ngx_uint_t             files_n;         /* Open file count */
    ngx_connection_t      *free_connections;
    ngx_uint_t             free_connection_n;
    ngx_module_t         **modules;         /* Loaded modules */
    ngx_uint_t             modules_n;       /* Module count */
    /* ... more fields ... */
};
```

### Startup Sequence

```
1. Parse command-line arguments
2. Read nginx.conf
3. Initialize modules (ngx_init_cycle)
4. Open listening sockets
5. Drop privileges (if configured)
6. Fork worker processes
7. Enter signal handling loop
```

---

## Worker Processes

Worker processes handle all client connections. Each worker:

- Runs as an **unprivileged user** (`worker_user` directive)
- Has its own **event loop**
- Processes requests **independently** (no IPC needed for most operations)
- Shares **listening sockets** with other workers

### Connection Handling

```
Worker Process Event Loop:
┌──────────────────────────────────────┐
│                                      │
│  ┌──────────────────────────────┐    │
│  │     Accept new connection    │◄───┼─── Listening socket ready
│  └──────────────┬───────────────┘    │
│                 │                    │
│                 ▼                    │
│  ┌──────────────────────────────┐    │
│  │    Read request headers      │◄───┼─── Read event
│  └──────────────┬───────────────┘    │
│                 │                    │
│                 ▼                    │
│  ┌──────────────────────────────┐    │
│  │    Process request phases    │    │
│  └──────────────┬───────────────┘    │
│                 │                    │
│                 ▼                    │
│  ┌──────────────────────────────┐    │
│  │     Send response            │◄───┼─── Write event
│  └──────────────┬───────────────┘    │
│                 │                    │
│                 ▼                    │
│  ┌──────────────────────────────┐    │
│  │   Close or keep-alive        │    │
│  └──────────────────────────────┘    │
│                                      │
└──────────────────────────────────────┘
```

### Worker Count

```nginx
worker_processes auto;  # One per CPU core (recommended)
worker_processes 4;     # Fixed count
```

The optimal count depends on workload:

- **CPU-bound** (SSL, compression): `worker_processes = CPU cores`
- **I/O-bound** (proxying): Can exceed core count
- **Mixed**: Start with `auto` and tune

### Accept Mutex

To prevent thundering herd when a new connection arrives:

```nginx
events {
    accept_mutex on;       # Serialize accept() across workers
    accept_mutex_delay 500ms;
}
```

With modern kernels (`EPOLLEXCLUSIVE`, `SO_REUSEPORT`), this is often unnecessary.

---

## Helper Processes

### Cache Manager

Manages the on-disk cache:

```
cache manager process:
  - Monitors cache size
  - Removes expired entries
  - Enforces max_size limits
```

### Cache Loader

Runs once at startup to load cache metadata:

```
cache loader process:
  - Reads cache directory
  - Populates shared memory index
  - Exits when done
```

---

## Signal Handling

### Signal Reference

| Signal | Command | Action |
|--------|---------|--------|
| `TERM`, `INT` | `nginx -s stop` | Fast shutdown |
| `QUIT` | `nginx -s quit` | Graceful shutdown |
| `HUP` | `nginx -s reload` | Reload configuration |
| `USR1` | `nginx -s reopen` | Reopen log files |
| `USR2` | - | Upgrade binary |
| `WINCH` | - | Graceful worker shutdown |

### Graceful Reload Process

```
1. Master receives HUP signal
2. Master parses new configuration
3. Master opens new listening sockets (if needed)
4. Master starts new worker processes
5. Master signals old workers to quit gracefully
6. Old workers finish current requests
7. Old workers exit
```

```
Timeline:
───────────────────────────────────────────────►
    │           │               │           │
    │  HUP      │  New workers  │  Old      │
    │  signal   │  started      │  workers  │
    │           │               │  exit     │
    ▼           ▼               ▼           ▼
[Master]    [Parse]        [Running]    [Done]
            [Config]       [Both old    
                          & new workers]
```

### Binary Upgrade (Zero Downtime)

```bash
# 1. Send USR2 to start new master
kill -USR2 $(cat /var/run/nginx.pid)

# 2. New master starts with .oldbin pid file
# 3. Gracefully shut down old master
kill -QUIT $(cat /var/run/nginx.pid.oldbin)
```

---

## Inter-Process Communication

### Shared Memory Zones

Workers share data through shared memory:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=addr:10m;

# Caching
proxy_cache_path /cache levels=1:2 keys_zone=cache:100m;
```

### Implementation

```c
/* Shared memory zone structure */
typedef struct {
    u_char              *addr;      /* Start address */
    size_t               size;      /* Zone size */
    ngx_str_t            name;      /* Zone name */
    ngx_log_t           *log;
    ngx_uint_t           exists;    /* Already exists flag */
} ngx_shm_zone_t;

/* Atomic operations for shared counters */
ngx_atomic_fetch_add(&shm->counter, 1);
```

---

## Configuration

### Worker Settings

```nginx
# Process management
worker_processes auto;
worker_cpu_affinity auto;        # Bind workers to CPUs
worker_priority -5;              # Nice value
worker_rlimit_nofile 65535;      # File descriptor limit

# User/group
user nginx nginx;

# Working directory
working_directory /var/lib/nginx;
```

### Event Settings

```nginx
events {
    worker_connections 4096;     # Max connections per worker
    multi_accept on;             # Accept all pending connections
    use epoll;                   # Event method (Linux)
}
```

---

## Debugging Process Issues

### Check Process Status

```bash
# List NGINX processes
ps aux | grep nginx

# Output:
# root     1234  master process /usr/sbin/nginx
# nginx    1235  worker process
# nginx    1236  worker process
# nginx    1237  cache manager process
```

### Worker Process Crash

If a worker crashes, the master automatically spawns a new one:

```
[alert] worker process 1235 exited on signal 11 (core dumped)
[notice] start worker process 1238
```

### Debug Logging

```nginx
error_log /var/log/nginx/error.log debug;

# Or per-connection debug
events {
    debug_connection 192.168.1.100;
}
```

---

## Best Practices

!!! tip "Production Recommendations"
    1. **Use `worker_processes auto`** - Matches CPU cores
    2. **Set appropriate `worker_connections`** - Calculate: `max_clients = worker_processes × worker_connections`
    3. **Enable `worker_cpu_affinity auto`** - Reduces cache misses
    4. **Use `worker_rlimit_nofile`** - Prevent "too many open files"
    5. **Monitor worker memory** - Watch for leaks in long-running processes
