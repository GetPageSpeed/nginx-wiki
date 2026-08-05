---
title: NGINX Configuration API - Directives and Parsing Reference
description: Complete guide to NGINX configuration API covering directive types, built-in handlers, custom parsers, and configuration merging for module development.
keywords: nginx configuration api, nginx directives, ngx_command_t, nginx config parsing, nginx conf, directive handlers
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - configuration
  - directives
  - config parsing
  - ngx_command_t
  - module development
---

# Configuration API

The Configuration API handles parsing nginx.conf directives and managing configuration structures.

---

## Directive Types

### Location Flags

```c
/* Where the directive is valid */
NGX_HTTP_MAIN_CONF    /* http { } block */
NGX_HTTP_SRV_CONF     /* server { } block */
NGX_HTTP_LOC_CONF     /* location { } block */
NGX_HTTP_LIF_CONF     /* location if { } block */

/* Argument count */
NGX_CONF_NOARGS       /* No arguments */
NGX_CONF_TAKE1        /* Exactly 1 argument */
NGX_CONF_TAKE2        /* Exactly 2 arguments */
NGX_CONF_TAKE3        /* Exactly 3 arguments */
NGX_CONF_TAKE12       /* 1 or 2 arguments */
NGX_CONF_TAKE123      /* 1, 2, or 3 arguments */
NGX_CONF_1MORE        /* At least 1 argument */
NGX_CONF_2MORE        /* At least 2 arguments */
NGX_CONF_FLAG         /* on|off flag */
NGX_CONF_BLOCK        /* Block directive { } */
```

---

## Built-in Directive Handlers

### Flags (on/off)

```c
/* Configuration */
typedef struct {
    ngx_flag_t  enable;
} ngx_http_mymodule_conf_t;

/* Directive */
{
    ngx_string("mymodule_enable"),
    NGX_HTTP_LOC_CONF | NGX_CONF_FLAG,
    ngx_conf_set_flag_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, enable),
    NULL
}

/* Initialize */
conf->enable = NGX_CONF_UNSET;

/* Merge */
ngx_conf_merge_value(conf->enable, prev->enable, 0);

/* Usage in nginx.conf: mymodule_enable on; */
```

### Strings

```c
typedef struct {
    ngx_str_t  name;
} ngx_http_mymodule_conf_t;

{
    ngx_string("mymodule_name"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_str_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, name),
    NULL
}

/* No special init needed for strings */

ngx_conf_merge_str_value(conf->name, prev->name, "default");

/* Usage: mymodule_name "my-value"; */
```

### Numbers

```c
typedef struct {
    ngx_uint_t  count;
    ngx_int_t   timeout;
    size_t      buffer_size;
    off_t       max_size;
    ngx_msec_t  interval;
} ngx_http_mymodule_conf_t;

/* Unsigned integer */
{
    ngx_string("mymodule_count"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_num_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, count),
    NULL
}

/* Size (supports k, m suffixes) */
{
    ngx_string("mymodule_buffer_size"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_size_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, buffer_size),
    NULL
}

/* Offset/file size (supports k, m, g suffixes) */
{
    ngx_string("mymodule_max_size"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_off_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, max_size),
    NULL
}

/* Milliseconds (supports s, m, h, d suffixes) */
{
    ngx_string("mymodule_interval"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
    ngx_conf_set_msec_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, interval),
    NULL
}

/* Initialize */
conf->count = NGX_CONF_UNSET_UINT;
conf->buffer_size = NGX_CONF_UNSET_SIZE;
conf->max_size = NGX_CONF_UNSET;
conf->interval = NGX_CONF_UNSET_MSEC;

/* Merge */
ngx_conf_merge_uint_value(conf->count, prev->count, 10);
ngx_conf_merge_size_value(conf->buffer_size, prev->buffer_size, 4096);
ngx_conf_merge_off_value(conf->max_size, prev->max_size, 1024 * 1024);
ngx_conf_merge_msec_value(conf->interval, prev->interval, 1000);
```

### Enums

```c
typedef struct {
    ngx_uint_t  method;
} ngx_http_mymodule_conf_t;

/* Define valid values */
static ngx_conf_enum_t ngx_http_mymodule_methods[] = {
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
    &ngx_http_mymodule_methods
}

/* Usage: mymodule_method advanced; */
```

### Bitmasks

```c
typedef struct {
    ngx_uint_t  options;
} ngx_http_mymodule_conf_t;

#define NGX_HTTP_MYMODULE_COMPRESS   0x0001
#define NGX_HTTP_MYMODULE_CACHE      0x0002
#define NGX_HTTP_MYMODULE_LOG        0x0004

static ngx_conf_bitmask_t ngx_http_mymodule_options[] = {
    { ngx_string("compress"), NGX_HTTP_MYMODULE_COMPRESS },
    { ngx_string("cache"), NGX_HTTP_MYMODULE_CACHE },
    { ngx_string("log"), NGX_HTTP_MYMODULE_LOG },
    { ngx_null_string, 0 }
};

{
    ngx_string("mymodule_options"),
    NGX_HTTP_LOC_CONF | NGX_CONF_1MORE,
    ngx_conf_set_bitmask_slot,
    NGX_HTTP_LOC_CONF_OFFSET,
    offsetof(ngx_http_mymodule_conf_t, options),
    &ngx_http_mymodule_options
}

/* Usage: mymodule_options compress cache; */

/* Check in code */
if (conf->options & NGX_HTTP_MYMODULE_COMPRESS) {
    /* compression enabled */
}
```

---

## Custom Directive Handlers

### Single Argument

```c
static char *
ngx_http_mymodule_custom(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_conf_t *mcf = conf;
    ngx_str_t *value;

    /* cf->args->elts[0] is the directive name */
    /* cf->args->elts[1] is the first argument */
    value = cf->args->elts;

    if (value[1].len == 0) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "empty value in \"%V\" directive", &value[0]);
        return NGX_CONF_ERROR;
    }

    mcf->custom_value = value[1];

    return NGX_CONF_OK;
}
```

### Multiple Arguments

```c
static char *
ngx_http_mymodule_pair(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_conf_t *mcf = conf;
    ngx_str_t *value;

    value = cf->args->elts;

    /* value[0] = directive name */
    /* value[1] = first argument (key) */
    /* value[2] = second argument (value) */

    mcf->key = value[1];
    mcf->val = value[2];

    return NGX_CONF_OK;
}

/* Directive definition */
{
    ngx_string("mymodule_pair"),
    NGX_HTTP_LOC_CONF | NGX_CONF_TAKE2,
    ngx_http_mymodule_pair,
    NGX_HTTP_LOC_CONF_OFFSET,
    0,
    NULL
}

/* Usage: mymodule_pair key value; */
```

### Block Directive

```c
static char *
ngx_http_mymodule_block(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_conf_t *mcf = conf;
    ngx_conf_t                save;
    char                     *rv;

    /* Parse arguments before block */
    ngx_str_t *value = cf->args->elts;
    mcf->block_name = value[1];

    /* Save current parser state */
    save = *cf;

    /* Set up parser for block contents */
    cf->handler = ngx_http_mymodule_block_handler;
    cf->handler_conf = conf;

    /* Parse block */
    rv = ngx_conf_parse(cf, NULL);

    /* Restore parser state */
    *cf = save;

    return rv;
}

static char *
ngx_http_mymodule_block_handler(ngx_conf_t *cf, ngx_command_t *dummy,
    void *conf)
{
    ngx_str_t *value = cf->args->elts;

    /* Handle directives inside block */
    if (ngx_strcmp(value[0].data, "item") == 0) {
        /* Process "item" directive */
        return NGX_CONF_OK;
    }

    ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                       "unknown directive \"%V\"", &value[0]);
    return NGX_CONF_ERROR;
}

/* Usage:
   mymodule_block name {
       item foo;
       item bar;
   }
*/
```

---

## Accessing Configuration

### In Handler

```c
static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_http_mymodule_main_conf_t *mmcf;
    ngx_http_mymodule_srv_conf_t  *mscf;
    ngx_http_mymodule_loc_conf_t  *mlcf;

    /* Get main config */
    mmcf = ngx_http_get_module_main_conf(r, ngx_http_mymodule_module);

    /* Get server config */
    mscf = ngx_http_get_module_srv_conf(r, ngx_http_mymodule_module);

    /* Get location config */
    mlcf = ngx_http_get_module_loc_conf(r, ngx_http_mymodule_module);

    if (!mlcf->enable) {
        return NGX_DECLINED;
    }

    /* ... */
}
```

### During Configuration

```c
static char *
ngx_http_mymodule_directive(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_loc_conf_t *mlcf = conf;
    ngx_http_core_loc_conf_t     *clcf;

    /* Get core location config */
    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);

    /* Access location name */
    ngx_conf_log_error(NGX_LOG_NOTICE, cf, 0,
                       "configuring for location: %V", &clcf->name);

    return NGX_CONF_OK;
}
```

---

## Validation Example

```c
static char *
ngx_http_mymodule_validate(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_mymodule_conf_t *mcf = conf;
    ngx_str_t *value = cf->args->elts;
    ngx_int_t  n;

    /* Parse number */
    n = ngx_atoi(value[1].data, value[1].len);
    if (n == NGX_ERROR) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "invalid number \"%V\"", &value[1]);
        return NGX_CONF_ERROR;
    }

    /* Validate range */
    if (n < 1 || n > 100) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "value %i is out of range [1-100]", n);
        return NGX_CONF_ERROR;
    }

    mcf->validated_number = n;

    return NGX_CONF_OK;
}
```
