---
title: NGINX HTTP API - Request Handling and Response Generation
description: Comprehensive HTTP API guide covering ngx_http_request_t, headers, body filters, subrequests, and response generation for NGINX module development.
keywords: nginx http api, ngx_http_request_t, nginx request handler, nginx response, nginx headers, nginx body filter, nginx subrequest
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - http
  - request handling
  - response generation
  - headers
  - filters
  - subrequests
---

# HTTP API

The HTTP API provides structures, constants, and functions for building HTTP modules.

---

## HTTP Status Codes

```c
NGX_HTTP_OK                    /* 200 */
NGX_HTTP_CREATED               /* 201 */
NGX_HTTP_NO_CONTENT            /* 204 */
NGX_HTTP_MOVED_PERMANENTLY     /* 301 */
NGX_HTTP_MOVED_TEMPORARILY     /* 302 */
NGX_HTTP_NOT_MODIFIED          /* 304 */
NGX_HTTP_BAD_REQUEST           /* 400 */
NGX_HTTP_UNAUTHORIZED          /* 401 */
NGX_HTTP_FORBIDDEN             /* 403 */
NGX_HTTP_NOT_FOUND             /* 404 */
NGX_HTTP_INTERNAL_SERVER_ERROR /* 500 */
NGX_HTTP_BAD_GATEWAY           /* 502 */
NGX_HTTP_SERVICE_UNAVAILABLE   /* 503 */
```

---

## Request Structure (`ngx_http_request_t`)

The central structure for HTTP processing:

```c
struct ngx_http_request_t {
    ngx_connection_t     *connection;   /* Client connection */
    ngx_pool_t           *pool;         /* Request memory pool */
    
    ngx_http_headers_in_t   headers_in;  /* Incoming headers */
    ngx_http_headers_out_t  headers_out; /* Outgoing headers */
    
    ngx_str_t  uri;          /* Request URI path */
    ngx_str_t  args;         /* Query string */
    ngx_str_t  method_name;  /* GET, POST, etc. */
    
    ngx_http_request_t  *main;    /* Main request */
    ngx_http_request_t  *parent;  /* Parent (for subrequests) */
    
    unsigned  header_only:1;  /* Only send headers */
    unsigned  internal:1;     /* Internal redirect */
    /* ... many more fields */
};
```

---

## Complete Handler Example

### Simple "Hello World" Handler

```c
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

static char *ngx_http_hello_world(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);
static ngx_int_t ngx_http_hello_world_handler(ngx_http_request_t *r);

/* Directive definition */
static ngx_command_t ngx_http_hello_world_commands[] = {
    {
        ngx_string("hello_world"),
        NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
        ngx_http_hello_world,
        0,
        0,
        NULL
    },
    ngx_null_command
};

/* Module context */
static ngx_http_module_t ngx_http_hello_world_module_ctx = {
    NULL,  /* preconfiguration */
    NULL,  /* postconfiguration */
    NULL,  /* create main configuration */
    NULL,  /* init main configuration */
    NULL,  /* create server configuration */
    NULL,  /* merge server configuration */
    NULL,  /* create location configuration */
    NULL   /* merge location configuration */
};

/* Module definition */
ngx_module_t ngx_http_hello_world_module = {
    NGX_MODULE_V1,
    &ngx_http_hello_world_module_ctx,
    ngx_http_hello_world_commands,
    NGX_HTTP_MODULE,
    NULL,  /* init master */
    NULL,  /* init module */
    NULL,  /* init process */
    NULL,  /* init thread */
    NULL,  /* exit thread */
    NULL,  /* exit process */
    NULL,  /* exit master */
    NGX_MODULE_V1_PADDING
};

/* Directive handler - sets up content handler */
static char *
ngx_http_hello_world(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;

    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_hello_world_handler;

    return NGX_CONF_OK;
}

/* Request handler */
static ngx_int_t
ngx_http_hello_world_handler(ngx_http_request_t *r)
{
    ngx_int_t    rc;
    ngx_buf_t   *b;
    ngx_chain_t  out;

    static u_char hello[] = "Hello, World!\n";

    /* Only handle GET and HEAD */
    if (!(r->method & (NGX_HTTP_GET | NGX_HTTP_HEAD))) {
        return NGX_HTTP_NOT_ALLOWED;
    }

    /* Discard request body */
    rc = ngx_http_discard_request_body(r);
    if (rc != NGX_OK) {
        return rc;
    }

    /* Set response headers */
    r->headers_out.status = NGX_HTTP_OK;
    r->headers_out.content_length_n = sizeof(hello) - 1;
    r->headers_out.content_type_len = sizeof("text/plain") - 1;
    ngx_str_set(&r->headers_out.content_type, "text/plain");

    /* Send headers */
    rc = ngx_http_send_header(r);
    if (rc == NGX_ERROR || rc > NGX_OK || r->header_only) {
        return rc;
    }

    /* Create response buffer */
    b = ngx_pcalloc(r->pool, sizeof(ngx_buf_t));
    if (b == NULL) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    b->pos = hello;
    b->last = hello + sizeof(hello) - 1;
    b->memory = 1;     /* Content is in read-only memory */
    b->last_buf = 1;   /* This is the last buffer */

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}
```

---

## Reading Request Headers

### Access Common Headers

```c
static ngx_int_t
ngx_http_check_headers(ngx_http_request_t *r)
{
    /* Host header (always present in HTTP/1.1) */
    if (r->headers_in.host) {
        ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                      "Host: %V", &r->headers_in.host->value);
    }

    /* User-Agent */
    if (r->headers_in.user_agent) {
        ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                      "User-Agent: %V", &r->headers_in.user_agent->value);
    }

    /* Content-Type */
    if (r->headers_in.content_type) {
        ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                      "Content-Type: %V", &r->headers_in.content_type->value);
    }

    /* Content-Length as number */
    if (r->headers_in.content_length_n > 0) {
        ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                      "Content-Length: %O", r->headers_in.content_length_n);
    }

    return NGX_OK;
}
```

### Search for Custom Headers

```c
static ngx_table_elt_t *
ngx_http_find_header(ngx_http_request_t *r, u_char *name, size_t len)
{
    ngx_list_part_t  *part;
    ngx_table_elt_t  *h;
    ngx_uint_t        i;

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

        if (len != h[i].key.len) {
            continue;
        }

        if (ngx_strncasecmp(name, h[i].key.data, len) == 0) {
            return &h[i];
        }
    }

    return NULL;
}

/* Usage */
static ngx_int_t
ngx_http_check_auth_token(ngx_http_request_t *r)
{
    ngx_table_elt_t *h;

    h = ngx_http_find_header(r, (u_char *) "X-Auth-Token", 12);
    if (h == NULL) {
        return NGX_HTTP_UNAUTHORIZED;
    }

    ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                  "Auth token: %V", &h->value);

    return NGX_OK;
}
```

---

## Setting Response Headers

### Add Custom Headers

```c
static ngx_int_t
ngx_http_add_custom_headers(ngx_http_request_t *r)
{
    ngx_table_elt_t *h;

    /* Add X-Powered-By header */
    h = ngx_list_push(&r->headers_out.headers);
    if (h == NULL) {
        return NGX_ERROR;
    }

    h->hash = 1;
    ngx_str_set(&h->key, "X-Powered-By");
    ngx_str_set(&h->value, "NGINX Module");

    /* Add X-Request-ID header with dynamic value */
    h = ngx_list_push(&r->headers_out.headers);
    if (h == NULL) {
        return NGX_ERROR;
    }

    h->hash = 1;
    ngx_str_set(&h->key, "X-Request-ID");
    
    /* Allocate value from pool */
    h->value.data = ngx_pnalloc(r->pool, 32);
    if (h->value.data == NULL) {
        return NGX_ERROR;
    }
    h->value.len = ngx_sprintf(h->value.data, "%016xD", 
                               (uint32_t) ngx_random()) - h->value.data;

    return NGX_OK;
}
```

---

## Subrequests

Execute internal requests to other locations:

```c
static ngx_int_t ngx_http_auth_subrequest_done(ngx_http_request_t *r,
    void *data, ngx_int_t rc);

static ngx_int_t
ngx_http_auth_check(ngx_http_request_t *r)
{
    ngx_http_request_t          *sr;
    ngx_http_post_subrequest_t  *ps;
    ngx_str_t                    uri;

    /* Allocate post-subrequest structure */
    ps = ngx_palloc(r->pool, sizeof(ngx_http_post_subrequest_t));
    if (ps == NULL) {
        return NGX_ERROR;
    }

    ps->handler = ngx_http_auth_subrequest_done;
    ps->data = r;

    /* Create subrequest to /auth endpoint */
    ngx_str_set(&uri, "/auth");

    if (ngx_http_subrequest(r, &uri, NULL, &sr, ps, 
                            NGX_HTTP_SUBREQUEST_WAITED) != NGX_OK) {
        return NGX_ERROR;
    }

    /* Don't send output from subrequest to client */
    sr->header_only = 1;

    return NGX_AGAIN;
}

static ngx_int_t
ngx_http_auth_subrequest_done(ngx_http_request_t *r, void *data, ngx_int_t rc)
{
    ngx_http_request_t *pr = data;  /* Parent request */

    /* Check subrequest result */
    if (r->headers_out.status == NGX_HTTP_OK) {
        /* Auth succeeded - continue processing parent */
        pr->write_event_handler = ngx_http_core_run_phases;
        return NGX_OK;
    }

    /* Auth failed */
    return NGX_HTTP_FORBIDDEN;
}
```

---

## Body Filters

Process response body before sending to client:

```c
static ngx_http_output_body_filter_pt ngx_http_next_body_filter;

static ngx_int_t
ngx_http_uppercase_body_filter(ngx_http_request_t *r, ngx_chain_t *in)
{
    ngx_chain_t *cl;
    ngx_buf_t   *b;
    u_char      *p;

    /* Process each buffer in the chain */
    for (cl = in; cl; cl = cl->next) {
        b = cl->buf;

        /* Only process memory buffers */
        if (!ngx_buf_in_memory(b)) {
            continue;
        }

        /* Convert to uppercase */
        for (p = b->pos; p < b->last; p++) {
            *p = ngx_toupper(*p);
        }
    }

    /* Pass to next filter */
    return ngx_http_next_body_filter(r, in);
}

/* Register filter in postconfiguration */
static ngx_int_t
ngx_http_uppercase_filter_init(ngx_conf_t *cf)
{
    ngx_http_next_body_filter = ngx_http_top_body_filter;
    ngx_http_top_body_filter = ngx_http_uppercase_body_filter;

    return NGX_OK;
}
```

---

## Reading Request Body

```c
static void ngx_http_mymodule_body_handler(ngx_http_request_t *r);

static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_int_t rc;

    /* Start reading body */
    rc = ngx_http_read_client_request_body(r, ngx_http_mymodule_body_handler);

    if (rc >= NGX_HTTP_SPECIAL_RESPONSE) {
        return rc;
    }

    return NGX_DONE;
}

static void
ngx_http_mymodule_body_handler(ngx_http_request_t *r)
{
    ngx_chain_t *cl;
    ngx_buf_t   *b;
    size_t       len = 0;

    if (r->request_body == NULL || r->request_body->bufs == NULL) {
        ngx_http_finalize_request(r, NGX_HTTP_INTERNAL_SERVER_ERROR);
        return;
    }

    /* Calculate total body length */
    for (cl = r->request_body->bufs; cl; cl = cl->next) {
        b = cl->buf;
        if (b->in_file) {
            len += b->file_last - b->file_pos;
        } else {
            len += b->last - b->pos;
        }
    }

    ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                  "received body: %uz bytes", len);

    /* Process body and send response */
    ngx_http_finalize_request(r, ngx_http_send_response(r));
}
```

---

## Common Patterns

### Return JSON Response

```c
static ngx_int_t
ngx_http_json_response(ngx_http_request_t *r, ngx_uint_t status,
                       const char *json)
{
    ngx_buf_t   *b;
    ngx_chain_t  out;
    size_t       len;

    len = ngx_strlen(json);

    r->headers_out.status = status;
    r->headers_out.content_length_n = len;
    ngx_str_set(&r->headers_out.content_type, "application/json");

    if (ngx_http_send_header(r) != NGX_OK) {
        return NGX_ERROR;
    }

    if (r->header_only) {
        return NGX_OK;
    }

    b = ngx_create_temp_buf(r->pool, len);
    if (b == NULL) {
        return NGX_ERROR;
    }

    ngx_memcpy(b->pos, json, len);
    b->last = b->pos + len;
    b->last_buf = 1;

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}

/* Usage */
return ngx_http_json_response(r, NGX_HTTP_OK, 
    "{\"status\":\"ok\",\"message\":\"Hello\"}");
```

### Internal Redirect

```c
static ngx_int_t
ngx_http_redirect_internal(ngx_http_request_t *r, ngx_str_t *uri)
{
    ngx_http_internal_redirect(r, uri, &r->args);
    return NGX_DONE;
}
```
