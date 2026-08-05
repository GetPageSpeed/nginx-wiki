---
title: NGINX HTTP Request Lifecycle - 11 Phases Explained
description: Complete guide to NGINX HTTP request processing phases, from connection accept through content generation and response filters.
keywords: nginx request lifecycle, nginx http phases, nginx request processing, nginx content handler, nginx filter chain, nginx subrequests
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - architecture
  - request lifecycle
  - HTTP phases
  - content handlers
  - filters
  - subrequests
  - module development
---

# HTTP Request Lifecycle

Every HTTP request in NGINX passes through a series of **phases**. Understanding this lifecycle is essential for module development and debugging.

---

## Request Flow Overview

```
Client                         NGINX                          Backend
  │                              │                               │
  │──── TCP Connect ────────────►│                               │
  │                              │                               │
  │──── HTTP Request ───────────►│                               │
  │                              │                               │
  │                    ┌─────────┴─────────┐                     │
  │                    │   Parse Headers   │                     │
  │                    └─────────┬─────────┘                     │
  │                              │                               │
  │                    ┌─────────┴─────────┐                     │
  │                    │  11 HTTP Phases   │                     │
  │                    └─────────┬─────────┘                     │
  │                              │                               │
  │                              │──── Proxy Request ───────────►│
  │                              │                               │
  │                              │◄─── Proxy Response ───────────│
  │                              │                               │
  │                    ┌─────────┴─────────┐                     │
  │                    │  Response Filters │                     │
  │                    └─────────┬─────────┘                     │
  │                              │                               │
  │◄──── HTTP Response ──────────│                               │
  │                              │                               │
```

---

## The 11 HTTP Phases

NGINX processes HTTP requests in 11 distinct phases:

```
┌──────────────────────────────────────────────────────────────┐
│                      HTTP Phases                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. NGX_HTTP_POST_READ_PHASE                                │
│     └── After reading request headers                        │
│                                                              │
│  2. NGX_HTTP_SERVER_REWRITE_PHASE                           │
│     └── Server-level rewrite directives                      │
│                                                              │
│  3. NGX_HTTP_FIND_CONFIG_PHASE        [internal]            │
│     └── Find matching location block                         │
│                                                              │
│  4. NGX_HTTP_REWRITE_PHASE                                  │
│     └── Location-level rewrite directives                    │
│                                                              │
│  5. NGX_HTTP_POST_REWRITE_PHASE       [internal]            │
│     └── Redirect to new location after rewrite               │
│                                                              │
│  6. NGX_HTTP_PREACCESS_PHASE                                │
│     └── Pre-access checks (limit_req, limit_conn)            │
│                                                              │
│  7. NGX_HTTP_ACCESS_PHASE                                   │
│     └── Access control (allow/deny, auth_basic)              │
│                                                              │
│  8. NGX_HTTP_POST_ACCESS_PHASE        [internal]            │
│     └── Access check result processing                       │
│                                                              │
│  9. NGX_HTTP_PRECONTENT_PHASE                               │
│     └── try_files, mirror                                    │
│                                                              │
│ 10. NGX_HTTP_CONTENT_PHASE                                  │
│     └── Content generation (proxy_pass, fastcgi, static)     │
│                                                              │
│ 11. NGX_HTTP_LOG_PHASE                                      │
│     └── Request logging                                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Phase Details

| # | Phase | Modules | Can Decline |
|---|-------|---------|-------------|
| 1 | `POST_READ` | realip | Yes |
| 2 | `SERVER_REWRITE` | rewrite | Yes |
| 3 | `FIND_CONFIG` | (core) | No |
| 4 | `REWRITE` | rewrite | Yes |
| 5 | `POST_REWRITE` | (core) | No |
| 6 | `PREACCESS` | limit_req, limit_conn | Yes |
| 7 | `ACCESS` | access, auth_basic, auth_request | Yes |
| 8 | `POST_ACCESS` | (core) | No |
| 9 | `PRECONTENT` | try_files, mirror | Yes |
| 10 | `CONTENT` | static, proxy, fastcgi | No |
| 11 | `LOG` | log | Yes |

---

## Phase Handler Return Values

```c
NGX_OK          /* Handler completed successfully */
NGX_DECLINED    /* Pass to next handler in phase */
NGX_AGAIN       /* Not ready, call again later */
NGX_DONE        /* Request will be finalized elsewhere */
NGX_ERROR       /* Error occurred */
NGX_HTTP_...    /* Return specific HTTP status code */
```

### Handler Behavior

```c
static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    /* Check if we should handle this request */
    if (!should_handle(r)) {
        return NGX_DECLINED;  /* Pass to next handler */
    }
    
    /* Check for errors */
    if (error_condition) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }
    
    /* Async operation pending */
    if (waiting_for_backend) {
        return NGX_AGAIN;
    }
    
    /* Request handled, response sent elsewhere */
    if (subrequest_started) {
        return NGX_DONE;
    }
    
    /* Successfully handled */
    return NGX_OK;
}
```

---

## Request Structure

The `ngx_http_request_t` structure holds all request state:

```c
struct ngx_http_request_t {
    /* Connection */
    ngx_connection_t         *connection;
    
    /* Request line */
    ngx_uint_t                method;        /* NGX_HTTP_GET, etc. */
    ngx_uint_t                http_version;  /* NGX_HTTP_VERSION_11 */
    ngx_str_t                 request_line;
    ngx_str_t                 uri;
    ngx_str_t                 args;
    ngx_str_t                 exten;         /* File extension */
    ngx_str_t                 unparsed_uri;
    
    /* Headers */
    ngx_http_headers_in_t     headers_in;
    ngx_http_headers_out_t    headers_out;
    
    /* Body */
    ngx_http_request_body_t  *request_body;
    
    /* Response */
    off_t                     headers_out.content_length_n;
    ngx_str_t                 headers_out.content_type;
    
    /* State */
    ngx_pool_t               *pool;
    ngx_http_request_t       *main;          /* Main request */
    ngx_http_request_t       *parent;        /* Parent (subrequest) */
    
    /* Configuration */
    void                    **ctx;           /* Module contexts */
    void                    **main_conf;
    void                    **srv_conf;
    void                    **loc_conf;
    
    /* Flags */
    unsigned                  internal:1;
    unsigned                  header_only:1;
    unsigned                  keepalive:1;
    unsigned                  chunked:1;
    /* ... many more ... */
};
```

---

## Detailed Phase Walkthrough

### 1. Connection Accept

```c
/* New connection callback */
static void
ngx_http_init_connection(ngx_connection_t *c)
{
    /* Set read handler to wait for request */
    c->read->handler = ngx_http_wait_request_handler;
    
    /* Add read timer */
    ngx_add_timer(c->read, cscf->client_header_timeout);
    
    /* Enable read event */
    ngx_handle_read_event(c->read, 0);
}
```

### 2. Parse Request Line

```
GET /path/to/resource?arg=value HTTP/1.1\r\n
│   │                 │          │
│   │                 │          └── http_version
│   │                 └── args
│   └── uri
└── method
```

### 3. Parse Headers

```
Host: example.com\r\n
User-Agent: Mozilla/5.0\r\n
Accept: text/html\r\n
\r\n
```

### 4. Run Phases

```c
void
ngx_http_core_run_phases(ngx_http_request_t *r)
{
    ngx_int_t                   rc;
    ngx_http_phase_handler_t   *ph;
    ngx_http_core_main_conf_t  *cmcf;

    cmcf = ngx_http_get_module_main_conf(r, ngx_http_core_module);
    ph = cmcf->phase_engine.handlers;

    while (ph[r->phase_handler].checker) {
        rc = ph[r->phase_handler].checker(r, &ph[r->phase_handler]);

        if (rc == NGX_OK) {
            return;
        }
    }
}
```

### 5. Content Generation

```
Content Handler Options:
├── ngx_http_static_module      → Serve static file
├── ngx_http_index_module       → Generate index
├── ngx_http_proxy_module       → Proxy to backend
├── ngx_http_fastcgi_module     → FastCGI backend
├── ngx_http_uwsgi_module       → uWSGI backend
├── ngx_http_grpc_module        → gRPC backend
└── Custom module handler       → Your code
```

### 6. Response Filters

Response passes through **filter chain**:

```
                     ┌──────────────────┐
                     │  Content Handler │
                     └────────┬─────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    Filter Chain                          │
│                                                          │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐      │
│  │   gzip     │ → │   SSI      │ → │  chunked   │ →    │
│  │   filter   │   │   filter   │   │   filter   │      │
│  └────────────┘   └────────────┘   └────────────┘      │
│                                                          │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐      │
│  │   headers  │ → │   range    │ → │   write    │ →    │
│  │   filter   │   │   filter   │   │   filter   │      │
│  └────────────┘   └────────────┘   └────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Send to Client  │
                     └──────────────────┘
```

---

## Subrequests

NGINX can create internal subrequests:

```c
ngx_int_t
ngx_http_subrequest(ngx_http_request_t *r,
    ngx_str_t *uri, ngx_str_t *args,
    ngx_http_request_t **psr,
    ngx_http_post_subrequest_t *ps,
    ngx_uint_t flags);
```

### Subrequest Flow

```
Main Request                    Subrequest
     │                              │
     │  ngx_http_subrequest()       │
     │ ─────────────────────────────► │
     │                              │
     │                        ┌─────┴─────┐
     │                        │ Run phases│
     │                        └─────┬─────┘
     │                              │
     │ ◄─────────────────────────── │
     │  Callback (ps->handler)      │
     │                              │
     ▼                              ▼
```

### Example: Auth Subrequest

```c
/* Create subrequest to /auth endpoint */
ngx_str_t uri = ngx_string("/auth");
ngx_http_post_subrequest_t *ps;

ps = ngx_palloc(r->pool, sizeof(ngx_http_post_subrequest_t));
ps->handler = ngx_http_auth_done;
ps->data = r;

ngx_http_subrequest(r, &uri, NULL, &sr, ps, NGX_HTTP_SUBREQUEST_WAITED);
```

---

## Internal Redirects

Location changes without client round-trip:

```c
/* Internal redirect to new URI */
ngx_http_internal_redirect(r, &new_uri, &r->args);

/* Named location redirect */
ngx_http_named_location(r, &name);
```

### try_files Implementation

```nginx
location / {
    try_files $uri $uri/ /index.php;
}
```

Translates to:

```
1. Try: /path/to/file
   └── Not found, continue

2. Try: /path/to/file/
   └── Not found, continue

3. Internal redirect: /index.php
   └── Restart phase processing
```

---

## Request Finalization

```c
void
ngx_http_finalize_request(ngx_http_request_t *r, ngx_int_t rc)
{
    /* Handle special return codes */
    if (rc == NGX_DONE) {
        /* Request already finalized elsewhere */
        return;
    }

    if (rc == NGX_DECLINED) {
        /* Pass to next phase handler */
        r->phase_handler++;
        ngx_http_core_run_phases(r);
        return;
    }

    if (rc >= NGX_HTTP_SPECIAL_RESPONSE) {
        /* Generate error page */
        ngx_http_finalize_request_error(r, rc);
        return;
    }

    /* Send response and close or keep-alive */
    ngx_http_finalize_connection(r);
}
```

---

## Debugging Request Flow

### Enable Debug Logging

```nginx
error_log /var/log/nginx/debug.log debug;
```

### Debug Output Example

```
[debug] http request line: "GET /index.html HTTP/1.1"
[debug] http uri: "/index.html"
[debug] http args: ""
[debug] http exten: "html"
[debug] generic phase: 0          # POST_READ
[debug] rewrite phase: 1          # SERVER_REWRITE
[debug] find config phase: 2      # FIND_CONFIG
[debug] using configuration "/"
[debug] rewrite phase: 3          # REWRITE
[debug] post rewrite phase: 4     # POST_REWRITE
[debug] generic phase: 5          # PREACCESS
[debug] generic phase: 6          # ACCESS
[debug] post access phase: 7      # POST_ACCESS
[debug] generic phase: 8          # PRECONTENT
[debug] content phase: 9          # CONTENT
[debug] http filename: "/var/www/html/index.html"
[debug] HTTP/1.1 200 OK
[debug] http output filter
[debug] http write filter
[debug] http log handler
```

---

## Best Practices

!!! tip "Request Processing Tips"
    1. **Understand phase order** - Critical for module placement
    2. **Return `NGX_DECLINED`** - If your handler shouldn't process the request
    3. **Don't block** - Use async operations for I/O
    4. **Use subrequests** - For auth checks, SSI includes
    5. **Leverage filters** - For response transformation
    6. **Log at debug level** - For troubleshooting flow issues
