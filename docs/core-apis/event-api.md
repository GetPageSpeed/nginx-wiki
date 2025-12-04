---
title: Event API
---

# Event API

NGINX's event-driven architecture is built on OS-level mechanisms (`epoll`, `kqueue`, `select`). Modules interact with the event loop through `ngx_event_t` and related functions.

---

## Event Structure

```c
struct ngx_event_t {
    void           *data;      /* User data (usually ngx_connection_t *) */
    ngx_event_handler_pt handler;  /* Callback when event fires */
    ngx_log_t      *log;       /* Log for this event */
    
    unsigned        ready:1;    /* Event is ready */
    unsigned        active:1;   /* Event is in the event queue */
    unsigned        timedout:1; /* Event timed out */
    unsigned        timer_set:1;/* Timer is set */
    unsigned        eof:1;      /* EOF received */
    unsigned        error:1;    /* Error occurred */
    /* ... more flags ... */
};

typedef void (*ngx_event_handler_pt)(ngx_event_t *ev);
```

---

## Timers

### One-Shot Timer

```c
static ngx_event_t   timer_event;
static ngx_connection_t  dumb_conn;  /* Required: event needs a connection */

static void
my_timer_handler(ngx_event_t *ev)
{
    ngx_log_error(NGX_LOG_INFO, ev->log, 0, "timer fired!");
    
    /* Re-arm timer for periodic execution */
    ngx_add_timer(ev, 5000);
}

static ngx_int_t
ngx_http_mymodule_init_process(ngx_cycle_t *cycle)
{
    ngx_memzero(&timer_event, sizeof(ngx_event_t));
    ngx_memzero(&dumb_conn, sizeof(ngx_connection_t));
    
    dumb_conn.fd = -1;  /* No real file descriptor */
    
    timer_event.handler = my_timer_handler;
    timer_event.log = cycle->log;
    timer_event.data = &dumb_conn;
    
    /* Fire after 5 seconds */
    ngx_add_timer(&timer_event, 5000);
    
    return NGX_OK;
}
```

### Cancelling a Timer

```c
static void
cancel_my_timer(void)
{
    if (timer_event.timer_set) {
        ngx_del_timer(&timer_event);
    }
}
```

### Request Timeout Example

```c
static void
ngx_http_mymodule_timeout_handler(ngx_event_t *ev)
{
    ngx_connection_t    *c = ev->data;
    ngx_http_request_t  *r = c->data;

    ngx_log_error(NGX_LOG_ERR, r->connection->log, 0,
                  "request timed out");
    
    ngx_http_finalize_request(r, NGX_HTTP_REQUEST_TIME_OUT);
}

static ngx_int_t
ngx_http_mymodule_set_timeout(ngx_http_request_t *r, ngx_msec_t timeout)
{
    ngx_event_t *wev = r->connection->write;
    
    /* Set timeout handler */
    wev->handler = ngx_http_mymodule_timeout_handler;
    
    /* Add timer */
    ngx_add_timer(wev, timeout);
    
    return NGX_OK;
}
```

---

## Connection Events

### Read Event Handler

```c
static void
ngx_http_mymodule_read_handler(ngx_event_t *rev)
{
    ngx_connection_t    *c = rev->data;
    ngx_http_request_t  *r = c->data;
    ssize_t              n;
    u_char               buf[4096];

    if (rev->timedout) {
        ngx_log_error(NGX_LOG_ERR, c->log, NGX_ETIMEDOUT,
                      "client timed out");
        ngx_http_finalize_request(r, NGX_HTTP_REQUEST_TIME_OUT);
        return;
    }

    for ( ;; ) {
        n = c->recv(c, buf, sizeof(buf));

        if (n == NGX_AGAIN) {
            /* No data available yet */
            if (ngx_handle_read_event(rev, 0) != NGX_OK) {
                ngx_http_finalize_request(r, NGX_HTTP_INTERNAL_SERVER_ERROR);
            }
            return;
        }

        if (n == 0) {
            /* Connection closed */
            ngx_log_error(NGX_LOG_INFO, c->log, 0,
                          "client closed connection");
            ngx_http_finalize_request(r, NGX_HTTP_CLIENT_CLOSED_REQUEST);
            return;
        }

        if (n < 0) {
            /* Error */
            ngx_http_finalize_request(r, NGX_HTTP_BAD_REQUEST);
            return;
        }

        /* Process n bytes in buf */
        ngx_log_error(NGX_LOG_DEBUG, c->log, 0,
                      "received %z bytes", n);
    }
}
```

### Write Event Handler

```c
static void
ngx_http_mymodule_write_handler(ngx_event_t *wev)
{
    ngx_connection_t    *c = wev->data;
    ngx_http_request_t  *r = c->data;
    ngx_chain_t         *out;
    ngx_int_t            rc;

    if (wev->timedout) {
        ngx_log_error(NGX_LOG_ERR, c->log, NGX_ETIMEDOUT, "write timed out");
        ngx_http_finalize_request(r, NGX_HTTP_REQUEST_TIME_OUT);
        return;
    }

    /* Get pending output chain from module context */
    ngx_http_mymodule_ctx_t *ctx;
    ctx = ngx_http_get_module_ctx(r, ngx_http_mymodule_module);
    out = ctx->out;

    if (out == NULL) {
        /* Nothing to send */
        if (wev->timer_set) {
            ngx_del_timer(wev);
        }
        ngx_http_finalize_request(r, NGX_OK);
        return;
    }

    /* Send data */
    rc = ngx_http_output_filter(r, out);

    if (rc == NGX_OK || rc == NGX_DONE) {
        ctx->out = NULL;
        ngx_http_finalize_request(r, rc);
        return;
    }

    if (rc == NGX_AGAIN) {
        /* Need to wait for socket to be writable */
        if (ngx_handle_write_event(wev, 0) != NGX_OK) {
            ngx_http_finalize_request(r, NGX_HTTP_INTERNAL_SERVER_ERROR);
        }
        return;
    }

    /* Error */
    ngx_http_finalize_request(r, rc);
}
```

---

## Event Loop Integration

### Adding Events to the Loop

```c
/* Add read event */
if (ngx_add_event(rev, NGX_READ_EVENT, NGX_LEVEL_EVENT) != NGX_OK) {
    return NGX_ERROR;
}

/* Add write event */
if (ngx_add_event(wev, NGX_WRITE_EVENT, NGX_LEVEL_EVENT) != NGX_OK) {
    return NGX_ERROR;
}
```

### Handling Events After Add

```c
/* After receiving data, re-arm read event */
if (ngx_handle_read_event(rev, 0) != NGX_OK) {
    return NGX_ERROR;
}

/* After sending data, re-arm write event if needed */
if (ngx_handle_write_event(wev, 0) != NGX_OK) {
    return NGX_ERROR;
}
```

### Removing Events

```c
/* Remove read event */
if (ngx_del_event(rev, NGX_READ_EVENT, NGX_CLOSE_EVENT) != NGX_OK) {
    return NGX_ERROR;
}
```

---

## Posted Events

Execute code later in the event loop iteration:

```c
static void
ngx_http_mymodule_posted_handler(ngx_event_t *ev)
{
    ngx_http_request_t *r = ev->data;
    
    /* Continue request processing */
    ngx_http_mymodule_continue(r);
}

static ngx_int_t
ngx_http_mymodule_defer_processing(ngx_http_request_t *r)
{
    ngx_event_t *ev;
    
    ev = ngx_pcalloc(r->pool, sizeof(ngx_event_t));
    if (ev == NULL) {
        return NGX_ERROR;
    }
    
    ev->handler = ngx_http_mymodule_posted_handler;
    ev->data = r;
    ev->log = r->connection->log;
    
    /* Post to be executed in next loop iteration */
    ngx_post_event(ev, &ngx_posted_events);
    
    return NGX_DONE;
}
```

---

## Complete Async Handler Example

```c
typedef struct {
    ngx_http_request_t  *request;
    ngx_event_t          timer;
    ngx_uint_t           state;
    u_char              *response;
    size_t               response_len;
} ngx_http_mymodule_ctx_t;

#define STATE_WAITING    0
#define STATE_PROCESSING 1
#define STATE_DONE       2

static void
ngx_http_mymodule_timer_handler(ngx_event_t *ev)
{
    ngx_http_mymodule_ctx_t *ctx = ev->data;
    ngx_http_request_t *r = ctx->request;

    ngx_log_error(NGX_LOG_DEBUG, r->connection->log, 0,
                  "async operation complete");

    ctx->state = STATE_DONE;

    /* Resume request processing */
    r->write_event_handler = ngx_http_core_run_phases;
    ngx_http_core_run_phases(r);
}

static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_http_mymodule_ctx_t *ctx;

    ctx = ngx_http_get_module_ctx(r, ngx_http_mymodule_module);

    if (ctx == NULL) {
        /* First call - start async operation */
        ctx = ngx_pcalloc(r->pool, sizeof(ngx_http_mymodule_ctx_t));
        if (ctx == NULL) {
            return NGX_HTTP_INTERNAL_SERVER_ERROR;
        }

        ctx->request = r;
        ctx->state = STATE_WAITING;
        
        ngx_http_set_ctx(r, ctx, ngx_http_mymodule_module);

        /* Simulate async operation with timer */
        ctx->timer.handler = ngx_http_mymodule_timer_handler;
        ctx->timer.data = ctx;
        ctx->timer.log = r->connection->log;
        
        ngx_add_timer(&ctx->timer, 100);  /* 100ms delay */

        /* Tell NGINX we're not done yet */
        r->main->count++;
        return NGX_DONE;
    }

    if (ctx->state != STATE_DONE) {
        /* Still waiting */
        return NGX_DONE;
    }

    /* Async operation complete - send response */
    return ngx_http_mymodule_send_response(r);
}
```

---

## Best Practices

!!! tip "Event Guidelines"
    1. **Always check `timedout`** - Handle timeout in every event handler
    2. **Use `NGX_AGAIN`** - Return this when waiting for I/O
    3. **Re-arm events** - Call `ngx_handle_read/write_event` after processing
    4. **Clean up timers** - Delete timers before finalizing requests
    5. **Increment `r->main->count`** - When deferring request processing
