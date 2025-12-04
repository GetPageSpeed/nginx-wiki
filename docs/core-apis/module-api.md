---
title: Module API
---

# Module API

This page describes the core structures and patterns for writing NGINX modules.

---

## Module Structure Overview

Every NGINX module consists of:

1. **Module definition** (`ngx_module_t`)
2. **Module context** (e.g., `ngx_http_module_t`)
3. **Commands** (`ngx_command_t[]`)
4. **Configuration structures** (main, server, location)
5. **Handlers/Filters** (the actual logic)

---

## Complete Module Skeleton

Here's a minimal but complete HTTP module:

```c
/*
 * ngx_http_example_module.c - A complete NGINX module example
 */

#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

/* ==================== Configuration Structures ==================== */

typedef struct {
    ngx_flag_t  enable;
    ngx_str_t   message;
    ngx_uint_t  count;
} ngx_http_example_loc_conf_t;

/* ==================== Function Declarations ==================== */

static ngx_int_t ngx_http_example_handler(ngx_http_request_t *r);
static void *ngx_http_example_create_loc_conf(ngx_conf_t *cf);
static char *ngx_http_example_merge_loc_conf(ngx_conf_t *cf,
    void *parent, void *child);
static char *ngx_http_example_set(ngx_conf_t *cf, ngx_command_t *cmd,
    void *conf);
static ngx_int_t ngx_http_example_init(ngx_conf_t *cf);

/* ==================== Directives ==================== */

static ngx_command_t ngx_http_example_commands[] = {

    /* example_enable on|off; */
    {
        ngx_string("example_enable"),
        NGX_HTTP_MAIN_CONF | NGX_HTTP_SRV_CONF | NGX_HTTP_LOC_CONF 
            | NGX_CONF_FLAG,
        ngx_conf_set_flag_slot,
        NGX_HTTP_LOC_CONF_OFFSET,
        offsetof(ngx_http_example_loc_conf_t, enable),
        NULL
    },

    /* example_message "string"; */
    {
        ngx_string("example_message"),
        NGX_HTTP_MAIN_CONF | NGX_HTTP_SRV_CONF | NGX_HTTP_LOC_CONF 
            | NGX_CONF_TAKE1,
        ngx_conf_set_str_slot,
        NGX_HTTP_LOC_CONF_OFFSET,
        offsetof(ngx_http_example_loc_conf_t, message),
        NULL
    },

    /* example_count <number>; */
    {
        ngx_string("example_count"),
        NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
        ngx_conf_set_num_slot,
        NGX_HTTP_LOC_CONF_OFFSET,
        offsetof(ngx_http_example_loc_conf_t, count),
        NULL
    },

    /* example; - activates the handler */
    {
        ngx_string("example"),
        NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
        ngx_http_example_set,
        NGX_HTTP_LOC_CONF_OFFSET,
        0,
        NULL
    },

    ngx_null_command
};

/* ==================== Module Context ==================== */

static ngx_http_module_t ngx_http_example_module_ctx = {
    NULL,                                /* preconfiguration */
    ngx_http_example_init,               /* postconfiguration */
    NULL,                                /* create main configuration */
    NULL,                                /* init main configuration */
    NULL,                                /* create server configuration */
    NULL,                                /* merge server configuration */
    ngx_http_example_create_loc_conf,    /* create location configuration */
    ngx_http_example_merge_loc_conf      /* merge location configuration */
};

/* ==================== Module Definition ==================== */

ngx_module_t ngx_http_example_module = {
    NGX_MODULE_V1,
    &ngx_http_example_module_ctx,        /* module context */
    ngx_http_example_commands,           /* module directives */
    NGX_HTTP_MODULE,                     /* module type */
    NULL,                                /* init master */
    NULL,                                /* init module */
    NULL,                                /* init process */
    NULL,                                /* init thread */
    NULL,                                /* exit thread */
    NULL,                                /* exit process */
    NULL,                                /* exit master */
    NGX_MODULE_V1_PADDING
};

/* ==================== Configuration Functions ==================== */

static void *
ngx_http_example_create_loc_conf(ngx_conf_t *cf)
{
    ngx_http_example_loc_conf_t *conf;

    conf = ngx_pcalloc(cf->pool, sizeof(ngx_http_example_loc_conf_t));
    if (conf == NULL) {
        return NULL;
    }

    conf->enable = NGX_CONF_UNSET;
    conf->count = NGX_CONF_UNSET_UINT;

    return conf;
}

static char *
ngx_http_example_merge_loc_conf(ngx_conf_t *cf, void *parent, void *child)
{
    ngx_http_example_loc_conf_t *prev = parent;
    ngx_http_example_loc_conf_t *conf = child;

    ngx_conf_merge_value(conf->enable, prev->enable, 0);
    ngx_conf_merge_str_value(conf->message, prev->message, "Hello!");
    ngx_conf_merge_uint_value(conf->count, prev->count, 1);

    return NGX_CONF_OK;
}

/* Directive handler that sets up content handler */
static char *
ngx_http_example_set(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;

    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_example_handler;

    return NGX_CONF_OK;
}

/* ==================== Request Handler ==================== */

static ngx_int_t
ngx_http_example_handler(ngx_http_request_t *r)
{
    ngx_int_t                     rc;
    ngx_buf_t                    *b;
    ngx_chain_t                   out;
    ngx_http_example_loc_conf_t  *elcf;
    u_char                       *response;
    size_t                        len;

    /* Get module configuration */
    elcf = ngx_http_get_module_loc_conf(r, ngx_http_example_module);

    /* Check if enabled */
    if (!elcf->enable) {
        return NGX_DECLINED;
    }

    /* Only handle GET/HEAD */
    if (!(r->method & (NGX_HTTP_GET | NGX_HTTP_HEAD))) {
        return NGX_HTTP_NOT_ALLOWED;
    }

    /* Discard request body */
    rc = ngx_http_discard_request_body(r);
    if (rc != NGX_OK) {
        return rc;
    }

    /* Allocate response buffer */
    len = elcf->message.len + 32;
    response = ngx_pnalloc(r->pool, len);
    if (response == NULL) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    /* Format response */
    len = ngx_snprintf(response, len, "%V (count=%ui)\n",
                       &elcf->message, elcf->count) - response;

    /* Set headers */
    r->headers_out.status = NGX_HTTP_OK;
    r->headers_out.content_length_n = len;
    r->headers_out.content_type_len = sizeof("text/plain") - 1;
    ngx_str_set(&r->headers_out.content_type, "text/plain");

    /* Send headers */
    rc = ngx_http_send_header(r);
    if (rc == NGX_ERROR || rc > NGX_OK || r->header_only) {
        return rc;
    }

    /* Create buffer */
    b = ngx_pcalloc(r->pool, sizeof(ngx_buf_t));
    if (b == NULL) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    b->pos = response;
    b->last = response + len;
    b->memory = 1;
    b->last_buf = 1;

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}

/* ==================== Initialization ==================== */

static ngx_int_t
ngx_http_example_init(ngx_conf_t *cf)
{
    /* Called after configuration is parsed */
    /* Use this for registering filters, phases, etc. */
    return NGX_OK;
}
```

---

## Configuration File Usage

```nginx
http {
    server {
        listen 80;
        
        location /example {
            example_enable on;
            example_message "Custom message";
            example_count 42;
            example;
        }
    }
}
```

---

## Key Structures

### `ngx_module_t`

```c
struct ngx_module_t {
    ngx_uint_t       ctx_index;     /* Index in context array */
    ngx_uint_t       index;         /* Module index */
    
    void            *ctx;           /* Module context */
    ngx_command_t   *commands;      /* Directives */
    ngx_uint_t       type;          /* NGX_HTTP_MODULE, etc. */
    
    /* Lifecycle callbacks */
    ngx_int_t      (*init_master)(ngx_log_t *log);
    ngx_int_t      (*init_module)(ngx_cycle_t *cycle);
    ngx_int_t      (*init_process)(ngx_cycle_t *cycle);
    ngx_int_t      (*init_thread)(ngx_cycle_t *cycle);
    void           (*exit_thread)(ngx_cycle_t *cycle);
    void           (*exit_process)(ngx_cycle_t *cycle);
    void           (*exit_master)(ngx_cycle_t *cycle);
};
```

### `ngx_command_t`

```c
struct ngx_command_t {
    ngx_str_t   name;    /* Directive name */
    ngx_uint_t  type;    /* Where valid + argument count */
    char      *(*set)(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);
    ngx_uint_t  conf;    /* NGX_HTTP_LOC_CONF_OFFSET, etc. */
    ngx_uint_t  offset;  /* offsetof() in config struct */
    void       *post;    /* Additional data */
};
```

### `ngx_http_module_t`

```c
typedef struct {
    ngx_int_t (*preconfiguration)(ngx_conf_t *cf);
    ngx_int_t (*postconfiguration)(ngx_conf_t *cf);
    
    void *(*create_main_conf)(ngx_conf_t *cf);
    char *(*init_main_conf)(ngx_conf_t *cf, void *conf);
    
    void *(*create_srv_conf)(ngx_conf_t *cf);
    char *(*merge_srv_conf)(ngx_conf_t *cf, void *prev, void *conf);
    
    void *(*create_loc_conf)(ngx_conf_t *cf);
    char *(*merge_loc_conf)(ngx_conf_t *cf, void *prev, void *conf);
} ngx_http_module_t;
```

---

## Related Documentation

- [Memory Management API](memory-api.md)
- [HTTP API](http-api.md)
- [Logging API](logging-api.md)
- [Configuration API](configuration-api.md)

---

## Building Your Module

### As Static Module

```bash
./configure --add-module=/path/to/your/module
make
```

### As Dynamic Module

```bash
./configure --add-dynamic-module=/path/to/your/module
make modules
```

Load in nginx.conf:

```nginx
load_module modules/ngx_http_example_module.so;
```
