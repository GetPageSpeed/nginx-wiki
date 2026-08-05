---
title: NGINX Module Configuration Directives - Developer Guide
description: Learn how to define custom configuration directives in NGINX modules. Covers directive types, handlers, and configuration merging.
keywords: NGINX directives, ngx_command_t, NGINX module config, configuration handlers, NGINX C API, directive types
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - module-development
  - configuration
  - directives
  - c-api
  - ngx_command_t
---

# Configuration Directives

This guide explains how to define custom directives in NGINX modules.

---

## Directive Structure

Every directive is defined by `ngx_command_t`:

```c
struct ngx_command_t {
    ngx_str_t             name;      /* Directive name */
    ngx_uint_t            type;      /* Where valid + argument count */
    char               *(*set)();    /* Handler function */
    ngx_uint_t            conf;      /* Configuration offset */
    ngx_uint_t            offset;    /* Field offset in struct */
    void                 *post;      /* Additional data */
};
```

---

## Directive Types

### Location Flags

Where the directive can appear:

```c
NGX_MAIN_CONF       /* Main context (outside blocks) */
NGX_EVENT_CONF      /* events { } block */
NGX_HTTP_MAIN_CONF  /* http { } block */
NGX_HTTP_SRV_CONF   /* server { } block */
NGX_HTTP_LOC_CONF   /* location { } block */
NGX_HTTP_UPS_CONF   /* upstream { } block */
NGX_HTTP_SIF_CONF   /* server if { } block */
NGX_HTTP_LIF_CONF   /* location if { } block */
NGX_HTTP_LMT_CONF   /* limit_except { } block */
```

### Argument Flags

```c
NGX_CONF_NOARGS     /* No arguments: directive; */
NGX_CONF_TAKE1      /* 1 argument: directive value; */
NGX_CONF_TAKE2      /* 2 arguments: directive val1 val2; */
NGX_CONF_TAKE3      /* 3 arguments */
NGX_CONF_TAKE4      /* 4 arguments */
NGX_CONF_TAKE5      /* 5 arguments */
NGX_CONF_TAKE6      /* 6 arguments */
NGX_CONF_TAKE7      /* 7 arguments */

NGX_CONF_TAKE12     /* 1 or 2 arguments */
NGX_CONF_TAKE13     /* 1 or 3 arguments */
NGX_CONF_TAKE23     /* 2 or 3 arguments */
NGX_CONF_TAKE123    /* 1, 2, or 3 arguments */
NGX_CONF_TAKE1234   /* 1 to 4 arguments */

NGX_CONF_1MORE      /* At least 1 argument */
NGX_CONF_2MORE      /* At least 2 arguments */

NGX_CONF_FLAG       /* on|off flag */
NGX_CONF_BLOCK      /* Block directive { } */
NGX_CONF_ANY        /* Any number of arguments */
```

---

## Built-in Handlers

NGINX provides handlers for common value types.

### Flag (on/off)

```c
typedef struct {
    ngx_flag_t enable;
} ngx_http_mymodule_conf_t;

static ngx_command_t commands[] = {
    {
        ngx_string("mymodule_enable"),
        NGX_HTTP_LOC_CONF | NGX_CONF_FLAG,
        ngx_conf_set_flag_slot,
        NGX_HTTP_LOC_CONF_OFFSET,
        offsetof(ngx_http_mymodule_conf_t, enable),
        NULL
    },
    ngx_null_command
};
```

Usage: `mymodule_enable on;` or `mymodule_enable off;`

### String

```c
typedef struct {
    ngx_str_t name;
} ngx_http_mymodule_conf_t;

{
    ngx_string("mymodule_name"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_str_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, name),
    NULL
}
```

Usage: `mymodule_name "my-value";`

### Number (unsigned)

```c
typedef struct {
    ngx_uint_t count;
} ngx_http_mymodule_conf_t;

{
    ngx_string("mymodule_count"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_num_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, count),
    NULL
}
```

Usage: `mymodule_count 10;`

### Size (with k/m suffix)

```c
typedef struct {
    size_t buffer_size;
} ngx_http_mymodule_conf_t;

{
    ngx_string("mymodule_buffer_size"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_size_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, buffer_size),
    NULL
}
```

Usage: `mymodule_buffer_size 4k;` or `mymodule_buffer_size 1m;`

### Time (with s/m/h/d suffix)

```c
typedef struct {
    ngx_msec_t timeout;
} ngx_http_mymodule_conf_t;

{
    ngx_string("mymodule_timeout"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_msec_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, timeout),
    NULL
}
```

Usage: `mymodule_timeout 30s;` or `mymodule_timeout 5m;`

### Enum

```c
typedef struct {
    ngx_uint_t method;
} ngx_http_mymodule_conf_t;

static ngx_conf_enum_t methods[] = {
    { ngx_string("simple"), 0 },
    { ngx_string("advanced"), 1 },
    { ngx_string("expert"), 2 },
    { ngx_null_string, 0 }
};

{
    ngx_string("mymodule_method"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_enum_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, method),
    &methods
}
```

Usage: `mymodule_method advanced;`

### Bitmask

```c
#define METHOD_GET     0x0001
#define METHOD_POST    0x0002
#define METHOD_PUT     0x0004
#define METHOD_DELETE  0x0008

typedef struct {
    ngx_uint_t methods;
} ngx_http_mymodule_conf_t;

static ngx_conf_bitmask_t method_masks[] = {
    { ngx_string("GET"), METHOD_GET },
    { ngx_string("POST"), METHOD_POST },
    { ngx_string("PUT"), METHOD_PUT },
    { ngx_string("DELETE"), METHOD_DELETE },
    { ngx_null_string, 0 }
};

{
    ngx_string("mymodule_methods"),
    NGX_HTTP_LOC_CONF | NGX_CONF_1MORE,
    ngx_conf_set_bitmask_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, methods),
    &method_masks
}
```

Usage: `mymodule_methods GET POST PUT;`

---

## Custom Handlers

For complex directives, write a custom handler:

### Single Argument

```c
static char *
ngx_http_mymodule_set_value(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_conf_t *mcf = conf;
    ngx_str_t *value;

    value = cf->args->elts;
    /* value[0] = directive name */
    /* value[1] = first argument */

    if (value[1].len == 0) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "empty value in \"%V\" directive", &value[0]);
        return NGX_CONF_ERROR;
    }

    mcf->my_value = value[1];

    return NGX_CONF_OK;
}
```

### Multiple Arguments

```c
static char *
ngx_http_mymodule_set_pair(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_conf_t *mcf = conf;
    ngx_str_t *value;
    ngx_int_t n;

    value = cf->args->elts;
    /* value[0] = directive name */
    /* value[1] = key */
    /* value[2] = val */

    mcf->key = value[1];

    n = ngx_atoi(value[2].data, value[2].len);
    if (n == NGX_ERROR || n < 0) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "invalid number \"%V\"", &value[2]);
        return NGX_CONF_ERROR;
    }

    mcf->val = n;

    return NGX_CONF_OK;
}

{
    ngx_string("mymodule_pair"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE2,
    ngx_http_mymodule_set_pair,
    NGX_HTTP_LOC_CONF_OFFSET,
    0,
    NULL
}
```

Usage: `mymodule_pair key 42;`

### Content Handler Directive

```c
static char *
ngx_http_mymodule_handler_cmd(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;

    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_mymodule_handler;

    return NGX_CONF_OK;
}

{
    ngx_string("mymodule"),
    NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
    ngx_http_mymodule_handler_cmd,
    0,
    0,
    NULL
}
```

Usage:
```nginx
location /api {
    mymodule;
}
```

---

## Configuration Contexts

### Creating Configuration

```c
static ngx_http_module_t ngx_http_mymodule_module_ctx = {
    NULL,                               /* preconfiguration */
    ngx_http_mymodule_init,             /* postconfiguration */

    ngx_http_mymodule_create_main_conf, /* create main configuration */
    ngx_http_mymodule_init_main_conf,   /* init main configuration */

    ngx_http_mymodule_create_srv_conf,  /* create server configuration */
    ngx_http_mymodule_merge_srv_conf,   /* merge server configuration */

    ngx_http_mymodule_create_loc_conf,  /* create location configuration */
    ngx_http_mymodule_merge_loc_conf    /* merge location configuration */
};
```

### Create Location Config

```c
static void *
ngx_http_mymodule_create_loc_conf(ngx_conf_t *cf)
{
    ngx_http_mymodule_conf_t *conf;

    conf = ngx_pcalloc(cf->pool, sizeof(ngx_http_mymodule_conf_t));
    if (conf == NULL) {
        return NULL;
    }

    /* Set unset values */
    conf->enable = NGX_CONF_UNSET;
    conf->count = NGX_CONF_UNSET_UINT;
    conf->timeout = NGX_CONF_UNSET_MSEC;
    conf->buffer_size = NGX_CONF_UNSET_SIZE;

    return conf;
}
```

### Merge Configuration

```c
static char *
ngx_http_mymodule_merge_loc_conf(ngx_conf_t *cf, void *parent, void *child)
{
    ngx_http_mymodule_conf_t *prev = parent;
    ngx_http_mymodule_conf_t *conf = child;

    ngx_conf_merge_value(conf->enable, prev->enable, 0);
    ngx_conf_merge_uint_value(conf->count, prev->count, 10);
    ngx_conf_merge_msec_value(conf->timeout, prev->timeout, 30000);
    ngx_conf_merge_size_value(conf->buffer_size, prev->buffer_size, 4096);
    ngx_conf_merge_str_value(conf->name, prev->name, "default");

    /* Validation */
    if (conf->count == 0) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "mymodule_count must be greater than 0");
        return NGX_CONF_ERROR;
    }

    return NGX_CONF_OK;
}
```

---

## Accessing Configuration

### At Runtime

```c
static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_http_mymodule_conf_t *conf;

    /* Get location config */
    conf = ngx_http_get_module_loc_conf(r, ngx_http_mymodule_module);

    if (!conf->enable) {
        return NGX_DECLINED;
    }

    /* Use conf->timeout, conf->buffer_size, etc. */
}
```

### During Configuration

```c
static char *
ngx_http_mymodule_directive(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;
    ngx_http_mymodule_main_conf_t *mmcf;

    /* Get core location config */
    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);

    /* Get our main config */
    mmcf = ngx_http_conf_get_module_main_conf(cf, ngx_http_mymodule_module);

    return NGX_CONF_OK;
}
```

---

## Merge Macros

```c
/* Flag (0 or 1) */
ngx_conf_merge_value(conf->enable, prev->enable, 0);

/* Unsigned int */
ngx_conf_merge_uint_value(conf->count, prev->count, 10);

/* Size */
ngx_conf_merge_size_value(conf->size, prev->size, 4096);

/* Milliseconds */
ngx_conf_merge_msec_value(conf->timeout, prev->timeout, 60000);

/* Seconds */
ngx_conf_merge_sec_value(conf->interval, prev->interval, 60);

/* String */
ngx_conf_merge_str_value(conf->name, prev->name, "default");

/* Pointer */
ngx_conf_merge_ptr_value(conf->handler, prev->handler, NULL);

/* Bitmask */
ngx_conf_merge_bitmask_value(conf->methods, prev->methods,
                             (NGX_CONF_BITMASK_SET | METHOD_GET));

/* Buffer */
ngx_conf_merge_bufs_value(conf->bufs, prev->bufs, 8, 4096);
```

---

## Complete Example

```c
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

typedef struct {
    ngx_flag_t  enable;
    ngx_str_t   message;
    ngx_uint_t  count;
    ngx_msec_t  timeout;
} ngx_http_example_loc_conf_t;

static void *ngx_http_example_create_loc_conf(ngx_conf_t *cf);
static char *ngx_http_example_merge_loc_conf(ngx_conf_t *cf,
    void *parent, void *child);
static char *ngx_http_example(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);
static ngx_int_t ngx_http_example_handler(ngx_http_request_t *r);

static ngx_command_t ngx_http_example_commands[] = {

    { ngx_string("example"),
      NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
      ngx_http_example,
      NGX_HTTP_LOC_CONF_OFFSET,
      0,
      NULL },

    { ngx_string("example_enable"),
      NGX_HTTP_MAIN_CONF | NGX_HTTP_SRV_CONF | NGX_HTTP_LOC_CONF | NGX_CONF_FLAG,
      ngx_conf_set_flag_slot,
      NGX_HTTP_LOC_CONF_OFFSET,
      offsetof(ngx_http_example_loc_conf_t, enable),
      NULL },

    { ngx_string("example_message"),
      NGX_HTTP_MAIN_CONF | NGX_HTTP_SRV_CONF | NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
      ngx_conf_set_str_slot,
      NGX_HTTP_LOC_CONF_OFFSET,
      offsetof(ngx_http_example_loc_conf_t, message),
      NULL },

    { ngx_string("example_count"),
      NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
      ngx_conf_set_num_slot,
      NGX_HTTP_LOC_CONF_OFFSET,
      offsetof(ngx_http_example_loc_conf_t, count),
      NULL },

    { ngx_string("example_timeout"),
      NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
      ngx_conf_set_msec_slot,
      NGX_HTTP_LOC_CONF_OFFSET,
      offsetof(ngx_http_example_loc_conf_t, timeout),
      NULL },

    ngx_null_command
};

static ngx_http_module_t ngx_http_example_module_ctx = {
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    ngx_http_example_create_loc_conf,
    ngx_http_example_merge_loc_conf
};

ngx_module_t ngx_http_example_module = {
    NGX_MODULE_V1,
    &ngx_http_example_module_ctx,
    ngx_http_example_commands,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

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
    conf->timeout = NGX_CONF_UNSET_MSEC;

    return conf;
}

static char *
ngx_http_example_merge_loc_conf(ngx_conf_t *cf, void *parent, void *child)
{
    ngx_http_example_loc_conf_t *prev = parent;
    ngx_http_example_loc_conf_t *conf = child;

    ngx_conf_merge_value(conf->enable, prev->enable, 1);
    ngx_conf_merge_str_value(conf->message, prev->message, "Hello!");
    ngx_conf_merge_uint_value(conf->count, prev->count, 1);
    ngx_conf_merge_msec_value(conf->timeout, prev->timeout, 30000);

    return NGX_CONF_OK;
}

static char *
ngx_http_example(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;

    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_example_handler;

    return NGX_CONF_OK;
}

static ngx_int_t
ngx_http_example_handler(ngx_http_request_t *r)
{
    ngx_http_example_loc_conf_t *conf;

    conf = ngx_http_get_module_loc_conf(r, ngx_http_example_module);

    if (!conf->enable) {
        return NGX_DECLINED;
    }

    /* Handler implementation... */
    return NGX_OK;
}
```

**nginx.conf usage:**

```nginx
http {
    example_message "Global message";

    server {
        example_message "Server message";

        location /api {
            example;
            example_enable on;
            example_count 5;
            example_timeout 60s;
        }
    }
}
```
