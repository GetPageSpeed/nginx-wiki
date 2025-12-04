---
title: Variables API
---

# Variables API

NGINX variables (`$variable_name`) are a powerful mechanism for passing data between modules and configuration. Modules can register custom variables and access existing ones.

---

## Variable Value Structure

```c
typedef struct {
    unsigned  len:28;        /* Value length */
    unsigned  valid:1;       /* Value is cached and valid */
    unsigned  no_cacheable:1;/* Re-evaluate each access */
    unsigned  not_found:1;   /* Variable not found */
    unsigned  escape:1;      /* Needs escaping */
    u_char   *data;          /* Value data */
} ngx_variable_value_t;
```

---

## Registering Variables

### Simple Variable

```c
static ngx_int_t ngx_http_mymodule_preconfiguration(ngx_conf_t *cf);
static ngx_int_t ngx_http_mymodule_request_count_variable(
    ngx_http_request_t *r, ngx_http_variable_value_t *v, uintptr_t data);

/* Module context */
static ngx_http_module_t ngx_http_mymodule_module_ctx = {
    ngx_http_mymodule_preconfiguration,  /* preconfiguration */
    NULL,                                 /* postconfiguration */
    /* ... */
};

/* Variable definition */
static ngx_http_variable_t ngx_http_mymodule_vars[] = {
    {
        ngx_string("mymodule_request_count"),
        NULL,  /* set handler */
        ngx_http_mymodule_request_count_variable,  /* get handler */
        0,     /* data */
        NGX_HTTP_VAR_NOCACHEABLE,  /* flags */
        0      /* index */
    },
    ngx_http_null_variable
};

/* Register variables */
static ngx_int_t
ngx_http_mymodule_preconfiguration(ngx_conf_t *cf)
{
    ngx_http_variable_t *var, *v;

    for (v = ngx_http_mymodule_vars; v->name.len; v++) {
        var = ngx_http_add_variable(cf, &v->name, v->flags);
        if (var == NULL) {
            return NGX_ERROR;
        }

        var->get_handler = v->get_handler;
        var->data = v->data;
    }

    return NGX_OK;
}

/* Get handler - called when $mymodule_request_count is accessed */
static ngx_int_t
ngx_http_mymodule_request_count_variable(ngx_http_request_t *r,
    ngx_http_variable_value_t *v, uintptr_t data)
{
    ngx_http_mymodule_ctx_t *ctx;
    u_char *p;

    ctx = ngx_http_get_module_ctx(r, ngx_http_mymodule_module);
    if (ctx == NULL) {
        v->not_found = 1;
        return NGX_OK;
    }

    /* Allocate space for number string */
    p = ngx_pnalloc(r->pool, NGX_INT_T_LEN);
    if (p == NULL) {
        return NGX_ERROR;
    }

    v->len = ngx_sprintf(p, "%ui", ctx->request_count) - p;
    v->valid = 1;
    v->no_cacheable = 0;
    v->not_found = 0;
    v->data = p;

    return NGX_OK;
}
```

### Variable with Set Handler

```c
static ngx_int_t
ngx_http_mymodule_var_set(ngx_http_request_t *r,
    ngx_http_variable_value_t *v, uintptr_t data)
{
    ngx_http_mymodule_ctx_t *ctx;

    ctx = ngx_http_get_module_ctx(r, ngx_http_mymodule_module);
    if (ctx == NULL) {
        ctx = ngx_pcalloc(r->pool, sizeof(ngx_http_mymodule_ctx_t));
        if (ctx == NULL) {
            return NGX_ERROR;
        }
        ngx_http_set_ctx(r, ctx, ngx_http_mymodule_module);
    }

    /* Store value in context */
    ctx->custom_value.len = v->len;
    ctx->custom_value.data = ngx_pstrdup(r->pool, 
        &(ngx_str_t){v->len, v->data});

    return NGX_OK;
}
```

---

## Accessing Variables at Runtime

### By Index (Fastest)

```c
typedef struct {
    ngx_int_t  remote_addr_index;
} ngx_http_mymodule_main_conf_t;

static ngx_int_t
ngx_http_mymodule_preconfiguration(ngx_conf_t *cf)
{
    ngx_http_mymodule_main_conf_t *mmcf;
    ngx_str_t name = ngx_string("remote_addr");

    mmcf = ngx_http_conf_get_module_main_conf(cf, ngx_http_mymodule_module);

    /* Get index for $remote_addr */
    mmcf->remote_addr_index = ngx_http_get_variable_index(cf, &name);
    if (mmcf->remote_addr_index == NGX_ERROR) {
        return NGX_ERROR;
    }

    return NGX_OK;
}

static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_http_mymodule_main_conf_t *mmcf;
    ngx_http_variable_value_t *vv;

    mmcf = ngx_http_get_module_main_conf(r, ngx_http_mymodule_module);

    /* Get value by index */
    vv = ngx_http_get_indexed_variable(r, mmcf->remote_addr_index);
    if (vv == NULL || vv->not_found) {
        ngx_log_error(NGX_LOG_ERR, r->connection->log, 0,
                      "remote_addr not found");
        return NGX_ERROR;
    }

    ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                  "client IP: %*s", vv->len, vv->data);

    return NGX_OK;
}
```

### By Name (Dynamic)

```c
static ngx_int_t
ngx_http_mymodule_get_var_by_name(ngx_http_request_t *r, ngx_str_t *name)
{
    ngx_uint_t key;
    ngx_http_variable_value_t *vv;

    /* Compute hash key */
    key = ngx_hash_strlow(name->data, name->data, name->len);

    /* Get variable */
    vv = ngx_http_get_variable(r, name, key);
    if (vv == NULL || vv->not_found) {
        return NGX_ERROR;
    }

    ngx_log_error(NGX_LOG_INFO, r->connection->log, 0,
                  "$%V = %*s", name, vv->len, vv->data);

    return NGX_OK;
}
```

### Force Re-evaluation

```c
/* For nocacheable variables, force fresh evaluation */
vv = ngx_http_get_flushed_variable(r, index);
```

---

## Variable Flags

| Flag | Description |
|------|-------------|
| `NGX_HTTP_VAR_CHANGEABLE` | Variable can be set via `set` directive |
| `NGX_HTTP_VAR_NOCACHEABLE` | Re-evaluate on each access |
| `NGX_HTTP_VAR_INDEXED` | Has a known index |
| `NGX_HTTP_VAR_NOHASH` | Cannot be accessed by name |
| `NGX_HTTP_VAR_PREFIX` | Prefix variable (e.g., `$arg_*`) |

---

## Complete Example: Request Timing Variable

```c
/*
 * Registers $mymodule_time variable showing request processing time
 */

#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

typedef struct {
    ngx_msec_t  start_time;
} ngx_http_mymodule_ctx_t;

static ngx_int_t ngx_http_mymodule_add_variables(ngx_conf_t *cf);
static ngx_int_t ngx_http_mymodule_time_variable(ngx_http_request_t *r,
    ngx_http_variable_value_t *v, uintptr_t data);
static ngx_int_t ngx_http_mymodule_init(ngx_conf_t *cf);

static ngx_http_variable_t ngx_http_mymodule_vars[] = {
    {
        ngx_string("mymodule_time"),
        NULL,
        ngx_http_mymodule_time_variable,
        0,
        NGX_HTTP_VAR_NOCACHEABLE,
        0
    },
    ngx_http_null_variable
};

static ngx_http_module_t ngx_http_mymodule_module_ctx = {
    ngx_http_mymodule_add_variables,
    ngx_http_mymodule_init,
    NULL, NULL, NULL, NULL, NULL, NULL
};

ngx_module_t ngx_http_mymodule_module = {
    NGX_MODULE_V1,
    &ngx_http_mymodule_module_ctx,
    NULL,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

static ngx_int_t
ngx_http_mymodule_add_variables(ngx_conf_t *cf)
{
    ngx_http_variable_t *var, *v;

    for (v = ngx_http_mymodule_vars; v->name.len; v++) {
        var = ngx_http_add_variable(cf, &v->name, v->flags);
        if (var == NULL) {
            return NGX_ERROR;
        }
        var->get_handler = v->get_handler;
        var->data = v->data;
    }

    return NGX_OK;
}

static ngx_int_t
ngx_http_mymodule_time_variable(ngx_http_request_t *r,
    ngx_http_variable_value_t *v, uintptr_t data)
{
    ngx_http_mymodule_ctx_t *ctx;
    ngx_msec_t elapsed;
    u_char *p;

    ctx = ngx_http_get_module_ctx(r, ngx_http_mymodule_module);
    if (ctx == NULL) {
        v->not_found = 1;
        return NGX_OK;
    }

    elapsed = ngx_current_msec - ctx->start_time;

    p = ngx_pnalloc(r->pool, NGX_TIME_T_LEN + 4);
    if (p == NULL) {
        return NGX_ERROR;
    }

    v->len = ngx_sprintf(p, "%M.%03M", 
                         elapsed / 1000, elapsed % 1000) - p;
    v->valid = 1;
    v->no_cacheable = 1;  /* Always recalculate */
    v->not_found = 0;
    v->data = p;

    return NGX_OK;
}

/* Handler to record start time */
static ngx_int_t
ngx_http_mymodule_handler(ngx_http_request_t *r)
{
    ngx_http_mymodule_ctx_t *ctx;

    ctx = ngx_pcalloc(r->pool, sizeof(ngx_http_mymodule_ctx_t));
    if (ctx == NULL) {
        return NGX_ERROR;
    }

    ctx->start_time = ngx_current_msec;
    ngx_http_set_ctx(r, ctx, ngx_http_mymodule_module);

    return NGX_DECLINED;
}

/* Register phase handler */
static ngx_int_t
ngx_http_mymodule_init(ngx_conf_t *cf)
{
    ngx_http_handler_pt *h;
    ngx_http_core_main_conf_t *cmcf;

    cmcf = ngx_http_conf_get_module_main_conf(cf, ngx_http_core_module);

    h = ngx_array_push(&cmcf->phases[NGX_HTTP_PREACCESS_PHASE].handlers);
    if (h == NULL) {
        return NGX_ERROR;
    }

    *h = ngx_http_mymodule_handler;

    return NGX_OK;
}
```

**Usage in nginx.conf:**

```nginx
log_format timing '$remote_addr - $request_time - $mymodule_time';
```
