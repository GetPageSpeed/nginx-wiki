---
title: NGINX Event Loop - Non-Blocking I/O and Concurrency Model
description: Understand NGINX event-driven architecture with epoll, kqueue, and non-blocking I/O that handles thousands of concurrent connections efficiently.
keywords: nginx event loop, nginx epoll, nginx kqueue, nginx non-blocking, nginx concurrency, nginx event-driven, nginx performance
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - architecture
  - event loop
  - epoll
  - kqueue
  - concurrency
  - non-blocking I/O
  - performance tuning
---

# Event Loop & Concurrency

NGINX handles thousands of concurrent connections using an **event-driven, non-blocking** architecture. Each worker process runs a single-threaded event loop.

---

## Why Event-Driven?

### Traditional Thread-per-Connection

```
Thread Model (Apache prefork):
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Thread 1 │ │ Thread 2 │ │ Thread N │
│ Client A │ │ Client B │ │ Client N │
│ (blocked)│ │ (blocked)│ │ (blocked)│
└──────────┘ └──────────┘ └──────────┘
     ↓             ↓             ↓
   Memory:      Memory:      Memory:
   ~1-8 MB      ~1-8 MB      ~1-8 MB
```

**Problems:**
- Memory overhead per connection
- Context switching cost
- Limited scalability (C10K problem)

### NGINX Event-Driven

```
Event Model (NGINX):
┌─────────────────────────────────────────┐
│            Single Thread                │
│  ┌─────┐ ┌─────┐ ┌─────┐     ┌─────┐   │
│  │ A   │ │ B   │ │ C   │ ... │ N   │   │
│  │ready│ │wait │ │ready│     │wait │   │
│  └──┬──┘ └─────┘ └──┬──┘     └─────┘   │
│     │               │                   │
│     └───────┬───────┘                   │
│             ▼                           │
│      Process ready events               │
└─────────────────────────────────────────┘
     ↓
   Memory: ~256 bytes per connection
```

**Benefits:**
- Minimal memory per connection
- No context switching
- Handles 10K+ connections per worker

---

## Event Mechanisms

NGINX uses OS-specific event notification APIs:

| OS | Mechanism | Directive |
|----|-----------|-----------|
| Linux 2.6+ | `epoll` | `use epoll;` |
| FreeBSD, macOS | `kqueue` | `use kqueue;` |
| Solaris | `/dev/poll` | `use /dev/poll;` |
| Windows | `IOCP` | (automatic) |
| Fallback | `select`/`poll` | `use select;` |

### epoll (Linux)

```c
/* NGINX epoll implementation (simplified) */
static ngx_int_t
ngx_epoll_process_events(ngx_cycle_t *cycle, ngx_msec_t timer,
    ngx_uint_t flags)
{
    int                events;
    ngx_event_t       *rev, *wev;
    struct epoll_event event_list[NGX_EPOLL_EVENTS];

    /* Wait for events */
    events = epoll_wait(ep, event_list, NGX_EPOLL_EVENTS, timer);

    for (i = 0; i < events; i++) {
        c = event_list[i].data.ptr;
        
        /* Handle read events */
        if (event_list[i].events & (EPOLLIN|EPOLLRDHUP)) {
            rev = c->read;
            rev->ready = 1;
            rev->handler(rev);
        }

        /* Handle write events */
        if (event_list[i].events & EPOLLOUT) {
            wev = c->write;
            wev->ready = 1;
            wev->handler(wev);
        }
    }

    return NGX_OK;
}
```

### kqueue (BSD/macOS)

```c
/* NGINX kqueue implementation (simplified) */
static ngx_int_t
ngx_kqueue_process_events(ngx_cycle_t *cycle, ngx_msec_t timer,
    ngx_uint_t flags)
{
    int                events;
    struct kevent      event_list[NGX_KQUEUE_EVENTS];
    struct timespec    ts;

    /* Wait for events */
    events = kevent(kq, NULL, 0, event_list, NGX_KQUEUE_EVENTS, &ts);

    for (i = 0; i < events; i++) {
        ev = event_list[i].udata;

        if (event_list[i].filter == EVFILT_READ) {
            ev->ready = 1;
            ev->handler(ev);
        }

        if (event_list[i].filter == EVFILT_WRITE) {
            ev->ready = 1;
            ev->handler(ev);
        }
    }

    return NGX_OK;
}
```

---

## Event Loop Structure

### Main Loop

```c
/* Worker process main loop (simplified) */
static void
ngx_worker_process_cycle(ngx_cycle_t *cycle, void *data)
{
    for ( ;; ) {
        /* Check for termination signal */
        if (ngx_terminate || ngx_quit) {
            ngx_worker_process_exit(cycle);
        }

        /* Process events with optional timer */
        ngx_process_events_and_timers(cycle);
    }
}

void
ngx_process_events_and_timers(ngx_cycle_t *cycle)
{
    ngx_msec_t  timer, delta;

    /* Find next timer expiration */
    timer = ngx_event_find_timer();

    /* Wait for events or timeout */
    delta = ngx_current_msec;
    (void) ngx_process_events(cycle, timer, flags);
    delta = ngx_current_msec - delta;

    /* Process expired timers */
    ngx_event_expire_timers();

    /* Process posted events */
    ngx_event_process_posted(cycle, &ngx_posted_accept_events);
    ngx_event_process_posted(cycle, &ngx_posted_events);
}
```

### Event Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    Event Loop Iteration                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────────┐                                    │
│   │ Calculate timer │ ◄─── Find nearest timer expiration │
│   └────────┬────────┘                                    │
│            │                                             │
│            ▼                                             │
│   ┌─────────────────┐                                    │
│   │   epoll_wait()  │ ◄─── Block until event or timeout  │
│   │   or kevent()   │                                    │
│   └────────┬────────┘                                    │
│            │                                             │
│            ▼                                             │
│   ┌─────────────────┐                                    │
│   │ Process events  │ ◄─── Call event handlers           │
│   └────────┬────────┘                                    │
│            │                                             │
│            ▼                                             │
│   ┌─────────────────┐                                    │
│   │ Expire timers   │ ◄─── Run timer callbacks           │
│   └────────┬────────┘                                    │
│            │                                             │
│            ▼                                             │
│   ┌─────────────────┐                                    │
│   │ Posted events   │ ◄─── Deferred event processing     │
│   └────────┬────────┘                                    │
│            │                                             │
│            └─────────────────► Next iteration            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Connection Structure

Each connection is represented by `ngx_connection_t`:

```c
struct ngx_connection_t {
    void               *data;           /* Request or other context */
    ngx_event_t        *read;           /* Read event */
    ngx_event_t        *write;          /* Write event */
    
    ngx_socket_t        fd;             /* Socket file descriptor */
    
    ngx_recv_pt         recv;           /* Receive function */
    ngx_send_pt         send;           /* Send function */
    ngx_recv_chain_pt   recv_chain;     /* Receive chain */
    ngx_send_chain_pt   send_chain;     /* Send chain */
    
    ngx_listening_t    *listening;      /* Listening socket */
    
    off_t               sent;           /* Bytes sent */
    
    ngx_log_t          *log;            /* Connection log */
    ngx_pool_t         *pool;           /* Connection memory pool */
    
    struct sockaddr    *sockaddr;       /* Client address */
    socklen_t           socklen;
    ngx_str_t           addr_text;      /* Client IP as string */
    
    ngx_buf_t          *buffer;         /* Read buffer */
    
    unsigned            buffered:8;     /* Buffered flags */
    unsigned            ssl:1;          /* SSL connection */
    unsigned            timedout:1;     /* Timed out */
    unsigned            error:1;        /* Error occurred */
    unsigned            destroyed:1;    /* Being destroyed */
    unsigned            close:1;        /* Close after response */
    /* ... more flags ... */
};
```

---

## Event Structure

```c
struct ngx_event_t {
    void            *data;          /* Usually ngx_connection_t */
    
    ngx_event_handler_pt  handler;  /* Event handler function */
    
    ngx_uint_t       index;         /* Event index */
    
    ngx_log_t       *log;           /* Event log */
    
    ngx_rbtree_node_t   timer;      /* Timer node (red-black tree) */
    
    unsigned         timedout:1;    /* Event timed out */
    unsigned         timer_set:1;   /* Timer is set */
    unsigned         ready:1;       /* Event is ready */
    unsigned         active:1;      /* Event is in queue */
    unsigned         disabled:1;    /* Event disabled */
    unsigned         pending_eof:1; /* EOF pending */
    unsigned         posted:1;      /* Posted for later */
    /* ... more flags ... */
};
```

---

## Timer Management

NGINX uses a **red-black tree** for efficient timer management:

```c
/* Add a timer */
ngx_add_timer(ev, timeout_ms);

/* Delete a timer */
ngx_del_timer(ev);

/* Timer callback */
static void
my_timeout_handler(ngx_event_t *ev)
{
    ngx_connection_t *c = ev->data;
    
    ngx_log_error(NGX_LOG_INFO, c->log, 0, "connection timed out");
    ngx_http_close_connection(c);
}
```

### Timer Resolution

```nginx
timer_resolution 100ms;  # Reduce gettimeofday() calls
```

---

## Posted Events

Events can be **posted** for deferred processing:

```c
/* Post an event */
ngx_post_event(ev, &ngx_posted_events);

/* Posted events are processed after the main event batch */
void
ngx_event_process_posted(ngx_cycle_t *cycle, ngx_queue_t *posted)
{
    ngx_queue_t  *q;
    ngx_event_t  *ev;

    while (!ngx_queue_empty(posted)) {
        q = ngx_queue_head(posted);
        ev = ngx_queue_data(q, ngx_event_t, queue);
        
        ngx_queue_remove(q);
        ev->handler(ev);
    }
}
```

### Use Cases

- **Accept events** - Processed before regular events
- **Cascading operations** - Prevent deep recursion
- **Lock release** - Continue after releasing mutex

---

## Non-Blocking I/O

All socket operations are non-blocking:

```c
/* Set socket to non-blocking */
if (ngx_nonblocking(s) == -1) {
    ngx_log_error(NGX_LOG_ALERT, log, ngx_socket_errno,
                  ngx_nonblocking_n " failed");
    return NGX_ERROR;
}

/* Receive data (returns immediately) */
n = c->recv(c, buf, size);

if (n == NGX_AGAIN) {
    /* No data available - wait for read event */
    ngx_handle_read_event(c->read, 0);
    return;
}

if (n == 0) {
    /* Connection closed */
    return;
}

if (n < 0) {
    /* Error */
    return;
}

/* Process n bytes */
```

---

## Configuration

```nginx
events {
    # Event mechanism
    use epoll;                    # Linux
    # use kqueue;                 # BSD/macOS
    
    # Connections per worker
    worker_connections 4096;
    
    # Accept multiple connections at once
    multi_accept on;
    
    # Serialize accept() (usually not needed)
    accept_mutex off;
    
    # Debug specific connections
    debug_connection 192.168.1.0/24;
}

# Reduce timer syscalls
timer_resolution 100ms;
```

---

## Performance Tuning

### System Limits

```bash
# Increase file descriptor limit
ulimit -n 65535

# Or in nginx.conf
worker_rlimit_nofile 65535;
```

### Kernel Parameters (Linux)

```bash
# /etc/sysctl.conf

# Increase connection backlog
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535

# TCP tuning
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1

# Buffer sizes
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
```

### SO_REUSEPORT (Linux 3.9+)

Allows multiple workers to bind to the same port:

```nginx
server {
    listen 80 reuseport;  # Each worker has own accept queue
}
```

Benefits:
- No accept mutex needed
- Better load distribution
- Reduced latency

---

## Debugging Events

### Enable Debug Logging

```nginx
error_log /var/log/nginx/debug.log debug;

events {
    debug_connection 192.168.1.100;
    debug_connection 192.168.1.0/24;
}
```

### Event Debug Output

```
[debug] epoll_wait() returned 3 events
[debug] epoll: fd:12 ev:0001 d:00007F8B12345678
[debug] http process request line
[debug] http request line: "GET /index.html HTTP/1.1"
```

---

## Best Practices

!!! tip "Event Loop Optimization"
    1. **Never block** - All operations must be non-blocking
    2. **Use appropriate event mechanism** - `epoll` on Linux, `kqueue` on BSD
    3. **Tune `worker_connections`** - Based on expected concurrency
    4. **Enable `reuseport`** - On Linux 3.9+ for better scaling
    5. **Set `timer_resolution`** - Reduce syscall overhead
    6. **Monitor event queue depth** - High values indicate bottleneck
