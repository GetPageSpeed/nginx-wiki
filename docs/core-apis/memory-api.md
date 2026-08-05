---
title: NGINX Memory Management API - Pools, Arrays, Buffers Guide
description: Master NGINX memory management with ngx_pool_t pools, ngx_array_t arrays, ngx_list_t lists, buffers, and cleanup handlers for leak-free modules.
keywords: nginx memory api, ngx_pool_t, nginx memory pool, ngx_palloc, ngx_array_t, nginx buffers, memory management
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - memory management
  - memory pools
  - buffers
  - arrays
  - cleanup handlers
---

# Memory Management API

NGINX uses **memory pools** for efficient, leak-free memory management. All request-scoped allocations use the request's pool and are automatically freed when the request completes.

---

## Pools (`ngx_pool_t`)

### Creating and Destroying Pools

```c
/* Create a pool with initial 4KB block */
ngx_pool_t *pool = ngx_create_pool(4096, log);
if (pool == NULL) {
    return NGX_ERROR;
}

/* Use the pool... */

/* Destroy when done (frees all memory allocated from it) */
ngx_destroy_pool(pool);
```

### Basic Allocation

```c
/* Allocate aligned memory (most common) */
my_struct_t *data = ngx_palloc(pool, sizeof(my_struct_t));

/* Allocate unaligned memory (slightly faster) */
u_char *buf = ngx_pnalloc(pool, 256);

/* Allocate and zero-initialize */
my_struct_t *data = ngx_pcalloc(pool, sizeof(my_struct_t));
```

### Complete Example: Custom Module Context

```c
typedef struct {
    ngx_str_t   value;
    ngx_flag_t  enabled;
    ngx_uint_t  count;
} ngx_http_mymodule_ctx_t;

static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_http_mymodule_ctx_t *ctx;

    /* Check if context already exists */
    ctx = ngx_http_get_module_ctx(r, ngx_http_mymodule_module);
    
    if (ctx == NULL) {
        /* Allocate from request pool - auto-freed when request ends */
        ctx = ngx_pcalloc(r->pool, sizeof(ngx_http_mymodule_ctx_t));
        if (ctx == NULL) {
            return NGX_ERROR;
        }
        
        /* Initialize */
        ctx->enabled = 1;
        ctx->count = 0;
        
        /* Store in request */
        ngx_http_set_ctx(r, ctx, ngx_http_mymodule_module);
    }
    
    ctx->count++;
    
    return NGX_DECLINED;
}
```

### Pool Cleanup Handlers

Register callbacks to run when the pool is destroyed:

```c
static void
ngx_http_mymodule_cleanup(void *data)
{
    ngx_http_mymodule_ctx_t *ctx = data;
    
    /* Close file handles, free external resources, etc. */
    if (ctx->fd != NGX_INVALID_FILE) {
        ngx_close_file(ctx->fd);
    }
}

static ngx_int_t
ngx_http_mymodule_init(ngx_http_request_t *r)
{
    ngx_pool_cleanup_t *cln;
    ngx_http_mymodule_ctx_t *ctx;
    
    ctx = ngx_pcalloc(r->pool, sizeof(ngx_http_mymodule_ctx_t));
    if (ctx == NULL) {
        return NGX_ERROR;
    }
    
    /* Register cleanup handler */
    cln = ngx_pool_cleanup_add(r->pool, 0);
    if (cln == NULL) {
        return NGX_ERROR;
    }
    
    cln->handler = ngx_http_mymodule_cleanup;
    cln->data = ctx;
    
    return NGX_OK;
}
```

---

## Arrays (`ngx_array_t`)

Growable arrays allocated from a pool.

### Creating and Using Arrays

```c
ngx_array_t *arr;
ngx_str_t   *name;

/* Create array for 4 initial elements */
arr = ngx_array_create(r->pool, 4, sizeof(ngx_str_t));
if (arr == NULL) {
    return NGX_ERROR;
}

/* Push elements */
name = ngx_array_push(arr);
if (name == NULL) {
    return NGX_ERROR;
}
ngx_str_set(name, "first");

name = ngx_array_push(arr);
if (name == NULL) {
    return NGX_ERROR;
}
ngx_str_set(name, "second");

/* Iterate over array */
ngx_str_t *names = arr->elts;
ngx_uint_t i;

for (i = 0; i < arr->nelts; i++) {
    ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                  "name[%ui]: %V", i, &names[i]);
}
```

### Real Example: Collecting Headers

```c
static ngx_int_t
ngx_http_collect_headers(ngx_http_request_t *r, ngx_array_t *headers)
{
    ngx_list_part_t  *part;
    ngx_table_elt_t  *h, *header;
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

        /* Push header into our array */
        header = ngx_array_push(headers);
        if (header == NULL) {
            return NGX_ERROR;
        }
        
        *header = h[i];
    }

    return NGX_OK;
}
```

---

## Lists (`ngx_list_t`)

Linked lists of fixed-size elements, ideal for headers.

```c
ngx_list_t      *list;
ngx_table_elt_t *h;

/* Create list for headers */
list = ngx_list_create(r->pool, 4, sizeof(ngx_table_elt_t));
if (list == NULL) {
    return NGX_ERROR;
}

/* Add a header */
h = ngx_list_push(list);
if (h == NULL) {
    return NGX_ERROR;
}

h->hash = 1;
ngx_str_set(&h->key, "X-Custom-Header");
ngx_str_set(&h->value, "custom-value");
```

---

## Buffers and Chains

### Creating a Response Buffer

```c
static ngx_int_t
ngx_http_mymodule_send_response(ngx_http_request_t *r)
{
    ngx_buf_t   *b;
    ngx_chain_t  out;
    ngx_int_t    rc;
    u_char      *response = (u_char *) "Hello, World!";
    size_t       len = ngx_strlen(response);

    /* Set response headers */
    r->headers_out.status = NGX_HTTP_OK;
    r->headers_out.content_length_n = len;
    ngx_str_set(&r->headers_out.content_type, "text/plain");

    /* Send headers */
    rc = ngx_http_send_header(r);
    if (rc == NGX_ERROR || rc > NGX_OK || r->header_only) {
        return rc;
    }

    /* Create buffer */
    b = ngx_create_temp_buf(r->pool, len);
    if (b == NULL) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    /* Copy data to buffer */
    ngx_memcpy(b->pos, response, len);
    b->last = b->pos + len;
    b->last_buf = 1;      /* This is the last buffer in the response */
    b->last_in_chain = 1;

    /* Create chain */
    out.buf = b;
    out.next = NULL;

    /* Send body */
    return ngx_http_output_filter(r, &out);
}
```

### Chaining Multiple Buffers

```c
static ngx_int_t
ngx_http_send_chunked_response(ngx_http_request_t *r)
{
    ngx_buf_t    *b1, *b2;
    ngx_chain_t  *out, *cl;

    /* First chunk */
    b1 = ngx_create_temp_buf(r->pool, 64);
    if (b1 == NULL) {
        return NGX_ERROR;
    }
    b1->last = ngx_sprintf(b1->pos, "First chunk\n");
    b1->last_buf = 0;

    /* Second chunk */
    b2 = ngx_create_temp_buf(r->pool, 64);
    if (b2 == NULL) {
        return NGX_ERROR;
    }
    b2->last = ngx_sprintf(b2->pos, "Second chunk\n");
    b2->last_buf = 1;
    b2->last_in_chain = 1;

    /* Link buffers into chain */
    out = ngx_alloc_chain_link(r->pool);
    if (out == NULL) {
        return NGX_ERROR;
    }
    out->buf = b1;

    cl = ngx_alloc_chain_link(r->pool);
    if (cl == NULL) {
        return NGX_ERROR;
    }
    cl->buf = b2;
    cl->next = NULL;

    out->next = cl;

    return ngx_http_output_filter(r, out);
}
```

---

## Best Practices

!!! tip "Memory Rules"
    1. **Always use pools** - Never use `malloc()`/`free()` directly
    2. **Use the right pool** - Request pool for request data, connection pool for connection data
    3. **Don't free individual allocations** - Pools free everything at once
    4. **Register cleanup handlers** for external resources (files, sockets)
    5. **Use `ngx_pcalloc`** when you need zero-initialized memory
