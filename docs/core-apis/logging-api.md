---
title: NGINX Logging API - Error Logging and Debug Messages Guide
description: Complete guide to NGINX logging API with ngx_log_error, debug macros, log levels, format specifiers, and custom log handlers for module development.
keywords: nginx logging api, ngx_log_error, nginx debug logging, nginx log levels, nginx error log, nginx log format
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - logging
  - debugging
  - error handling
  - log levels
  - module development
---

# Logging API

NGINX provides a powerful logging system for diagnostics and debugging.

---

## Log Levels

```c
NGX_LOG_STDERR   /* 0 - Errors to stderr before log is opened */
NGX_LOG_EMERG    /* 1 - System unusable */
NGX_LOG_ALERT    /* 2 - Immediate action required */
NGX_LOG_CRIT     /* 3 - Critical conditions */
NGX_LOG_ERR      /* 4 - Error conditions */
NGX_LOG_WARN     /* 5 - Warning conditions */
NGX_LOG_NOTICE   /* 6 - Normal but significant */
NGX_LOG_INFO     /* 7 - Informational */
NGX_LOG_DEBUG    /* 8 - Debug messages */
```

## Debug Categories

When NGINX is built with `--with-debug`:

```c
NGX_LOG_DEBUG_CORE
NGX_LOG_DEBUG_ALLOC
NGX_LOG_DEBUG_MUTEX
NGX_LOG_DEBUG_EVENT
NGX_LOG_DEBUG_HTTP
NGX_LOG_DEBUG_MAIL
NGX_LOG_DEBUG_STREAM
```

---

## Basic Logging

### Error Logging

```c
/* Simple message */
ngx_log_error(NGX_LOG_ERR, r->connection->log, 0,
              "something went wrong");

/* With system error code */
ngx_log_error(NGX_LOG_ERR, r->connection->log, ngx_errno,
              "failed to open file \"%s\"", filename);

/* With formatted values */
ngx_log_error(NGX_LOG_WARN, r->connection->log, 0,
              "request took %M ms, uri: %V", 
              elapsed_ms, &r->uri);
```

### Format Specifiers

| Specifier | Type | Description |
|-----------|------|-------------|
| `%d`, `%i` | `int` | Signed integer |
| `%ud`, `%ui` | `unsigned int` | Unsigned integer |
| `%l` | `long` | Long integer |
| `%ul` | `unsigned long` | Unsigned long |
| `%O` | `off_t` | File offset |
| `%z` | `ssize_t` | Signed size |
| `%uz` | `size_t` | Unsigned size |
| `%p` | `void *` | Pointer (hex) |
| `%s` | `char *` | C string |
| `%V` | `ngx_str_t *` | NGINX string |
| `%M` | `ngx_msec_t` | Milliseconds |
| `%T` | `time_t` | Time value |
| `%xd`, `%xD` | `int`, `uint32_t` | Hex |

---

## Practical Examples

### Request Handler Logging

```c
static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_log_t *log = r->connection->log;

    /* Info about request */
    ngx_log_error(NGX_LOG_INFO, log, 0,
                  "processing request: method=%V uri=%V args=%V",
                  &r->method_name, &r->uri, &r->args);

    /* Log client info */
    ngx_log_error(NGX_LOG_INFO, log, 0,
                  "client: %V, server: %V",
                  &r->connection->addr_text,
                  &r->headers_in.server);

    /* Log content length */
    if (r->headers_in.content_length_n > 0) {
        ngx_log_error(NGX_LOG_INFO, log, 0,
                      "content-length: %O",
                      r->headers_in.content_length_n);
    }

    return NGX_OK;
}
```

### Error Handling with Context

```c
static ngx_int_t
ngx_http_open_cache_file(ngx_http_request_t *r, ngx_str_t *path)
{
    ngx_fd_t fd;

    fd = ngx_open_file(path->data, NGX_FILE_RDONLY, 
                       NGX_FILE_OPEN, 0);

    if (fd == NGX_INVALID_FILE) {
        ngx_log_error(NGX_LOG_ERR, r->connection->log, ngx_errno,
                      ngx_open_file_n " \"%V\" failed", path);
        return NGX_ERROR;
    }

    ngx_log_error(NGX_LOG_DEBUG, r->connection->log, 0,
                  "cache file opened: %V, fd=%d", path, fd);

    return NGX_OK;
}
```

---

## Debug Logging

Debug logging is only compiled in when NGINX is built with `--with-debug`.

### Using Debug Macros

```c
/* Fixed argument count variants (more efficient) */
ngx_log_debug0(NGX_LOG_DEBUG_HTTP, log, 0, "handler called");

ngx_log_debug1(NGX_LOG_DEBUG_HTTP, log, 0,
               "uri: %V", &r->uri);

ngx_log_debug2(NGX_LOG_DEBUG_HTTP, log, 0,
               "method=%V uri=%V", &r->method_name, &r->uri);

ngx_log_debug3(NGX_LOG_DEBUG_HTTP, log, 0,
               "client=%V server=%V uri=%V",
               &r->connection->addr_text,
               &r->headers_in.server,
               &r->uri);

/* Up to ngx_log_debug8 available */
```

### Conditional Debug Logging

```c
static ngx_int_t
ngx_http_mymodule_process(ngx_http_request_t *r)
{
    ngx_msec_t start, elapsed;

#if (NGX_DEBUG)
    start = ngx_current_msec;
#endif

    /* Do processing... */

#if (NGX_DEBUG)
    elapsed = ngx_current_msec - start;
    ngx_log_debug1(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
                   "processing took %M ms", elapsed);
#endif

    return NGX_OK;
}
```

---

## Configuration-Time Logging

Use during config parsing:

```c
static char *
ngx_http_mymodule_set_value(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_str_t *value = cf->args->elts;

    if (value[1].len == 0) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "empty value in \"%V\" directive",
                           &cmd->name);
        return NGX_CONF_ERROR;
    }

    if (value[1].len > 1024) {
        ngx_conf_log_error(NGX_LOG_WARN, cf, 0,
                           "value too long in \"%V\" directive, "
                           "truncating to 1024 bytes",
                           &cmd->name);
    }

    return NGX_CONF_OK;
}
```

---

## Logging Incoming Data

### Log Request Headers

```c
static void
ngx_http_log_request_headers(ngx_http_request_t *r)
{
    ngx_list_part_t  *part;
    ngx_table_elt_t  *h;
    ngx_uint_t        i;

    ngx_log_error(NGX_LOG_DEBUG, r->connection->log, 0,
                  "=== Request Headers ===");

    part = &r->headers_in.headers.part;
    h = part->elts;

    for (i = 0; /* void */; i++) {
        if (i >= part->nelts) {
            if (part->next == NULL) {
                break;
            }
            part = part->next;
            h = part->elts;
            i = 0;
        }

        ngx_log_error(NGX_LOG_DEBUG, r->connection->log, 0,
                      "  %V: %V", &h[i].key, &h[i].value);
    }
}
```

### Log Binary Data (Hex Dump)

```c
static void
ngx_http_log_body_hex(ngx_http_request_t *r, u_char *data, size_t len)
{
    u_char  buf[64];
    u_char *p;
    size_t  i;

    ngx_log_error(NGX_LOG_DEBUG, r->connection->log, 0,
                  "body hex dump (%uz bytes):", len);

    for (i = 0; i < len; i += 16) {
        p = buf;
        
        for (size_t j = 0; j < 16 && i + j < len; j++) {
            p = ngx_sprintf(p, "%02xd ", data[i + j]);
        }
        
        ngx_log_error(NGX_LOG_DEBUG, r->connection->log, 0,
                      "  %04xd: %s", i, buf);
    }
}
```

---

## Custom Log Handler

For special logging needs:

```c
typedef struct {
    ngx_str_t   prefix;
    ngx_uint_t  request_count;
} ngx_http_mymodule_log_ctx_t;

static u_char *
ngx_http_mymodule_log_handler(ngx_log_t *log, u_char *buf, size_t len)
{
    ngx_http_mymodule_log_ctx_t *ctx = log->data;
    u_char *p = buf;

    if (ctx) {
        p = ngx_snprintf(buf, len, "[%V #%ui] ",
                         &ctx->prefix, ctx->request_count);
    }

    return p;
}

/* Attach custom handler to log */
static void
ngx_http_mymodule_setup_log(ngx_http_request_t *r)
{
    ngx_http_mymodule_log_ctx_t *ctx;

    ctx = ngx_pcalloc(r->pool, sizeof(ngx_http_mymodule_log_ctx_t));
    if (ctx == NULL) {
        return;
    }

    ngx_str_set(&ctx->prefix, "mymodule");
    ctx->request_count = 1;

    r->connection->log->handler = ngx_http_mymodule_log_handler;
    r->connection->log->data = ctx;
}
```

---

## Best Practices

!!! tip "Logging Guidelines"
    1. **Use appropriate levels** - Don't use `ERR` for non-errors
    2. **Include context** - Add request URI, client IP when relevant
    3. **Use `ngx_errno`** - Pass system error codes for I/O operations
    4. **Guard debug logging** - Use `#if (NGX_DEBUG)` for expensive debug code
    5. **Use fixed-argument macros** - `ngx_log_debug1` is faster than variadic
