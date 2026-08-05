---
title: NGINX Module Examples - Complete Working Code Samples
description: Working NGINX module examples including Hello World handler, JSON echo, access phase module, and response filters with full source code.
keywords: NGINX module examples, NGINX hello world, HTTP handler module, NGINX filter module, NGINX C code examples, access phase
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - module-examples
  - http-handler
  - filter-module
  - access-phase
  - c-programming
  - source-code
---

# Module Examples

Complete, working NGINX module examples you can study and build upon.

---

## Example 1: Hello World Handler

The simplest possible HTTP module - returns "Hello, World!".

### Source Code

```c
/* ngx_http_hello_module.c */
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

static char *ngx_http_hello(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);
static ngx_int_t ngx_http_hello_handler(ngx_http_request_t *r);

static ngx_command_t ngx_http_hello_commands[] = {
    {
        ngx_string("hello"),
        NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
        ngx_http_hello,
        0,
        0,
        NULL
    },
    ngx_null_command
};

static ngx_http_module_t ngx_http_hello_module_ctx = {
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
};

ngx_module_t ngx_http_hello_module = {
    NGX_MODULE_V1,
    &ngx_http_hello_module_ctx,
    ngx_http_hello_commands,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

static char *
ngx_http_hello(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;

    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_hello_handler;

    return NGX_CONF_OK;
}

static ngx_int_t
ngx_http_hello_handler(ngx_http_request_t *r)
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
    b->memory = 1;
    b->last_buf = 1;

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}
```

### Config File

```bash
# config
ngx_addon_name=ngx_http_hello_module
ngx_module_type=HTTP
ngx_module_name=ngx_http_hello_module
ngx_module_srcs="$ngx_addon_dir/ngx_http_hello_module.c"
. auto/module
```

### Usage

```nginx
location /hello {
    hello;
}
```

---

## Example 2: JSON Echo Handler

Returns request information as JSON.

### Source Code

```c
/* ngx_http_echo_json_module.c */
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

static char *ngx_http_echo_json(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);
static ngx_int_t ngx_http_echo_json_handler(ngx_http_request_t *r);

static ngx_command_t ngx_http_echo_json_commands[] = {
    {
        ngx_string("echo_json"),
        NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
        ngx_http_echo_json,
        0,
        0,
        NULL
    },
    ngx_null_command
};

static ngx_http_module_t ngx_http_echo_json_module_ctx = {
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
};

ngx_module_t ngx_http_echo_json_module = {
    NGX_MODULE_V1,
    &ngx_http_echo_json_module_ctx,
    ngx_http_echo_json_commands,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

static char *
ngx_http_echo_json(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;
    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_echo_json_handler;
    return NGX_CONF_OK;
}

static ngx_int_t
ngx_http_echo_json_handler(ngx_http_request_t *r)
{
    ngx_int_t    rc;
    ngx_buf_t   *b;
    ngx_chain_t  out;
    size_t       len;
    u_char      *json, *p;

    if (!(r->method & (NGX_HTTP_GET | NGX_HTTP_HEAD))) {
        return NGX_HTTP_NOT_ALLOWED;
    }

    rc = ngx_http_discard_request_body(r);
    if (rc != NGX_OK) {
        return rc;
    }

    /* Calculate JSON length */
    len = sizeof("{\"method\":\"\",\"uri\":\"\",\"args\":\"\",\"host\":\"\"}") - 1
          + r->method_name.len
          + r->uri.len
          + r->args.len
          + (r->headers_in.host ? r->headers_in.host->value.len : 0);

    /* Allocate buffer */
    json = ngx_pnalloc(r->pool, len + 100);  /* Extra space for escaping */
    if (json == NULL) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    /* Build JSON */
    p = ngx_sprintf(json,
        "{\"method\":\"%V\",\"uri\":\"%V\",\"args\":\"%V\",\"host\":\"%V\"}",
        &r->method_name,
        &r->uri,
        &r->args,
        r->headers_in.host ? &r->headers_in.host->value : &(ngx_str_t)ngx_string(""));

    len = p - json;

    /* Set headers */
    r->headers_out.status = NGX_HTTP_OK;
    r->headers_out.content_length_n = len;
    ngx_str_set(&r->headers_out.content_type, "application/json");

    rc = ngx_http_send_header(r);
    if (rc == NGX_ERROR || rc > NGX_OK || r->header_only) {
        return rc;
    }

    /* Create buffer */
    b = ngx_pcalloc(r->pool, sizeof(ngx_buf_t));
    if (b == NULL) {
        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    b->pos = json;
    b->last = json + len;
    b->memory = 1;
    b->last_buf = 1;

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}
```

### Output

```bash
curl http://localhost/echo
# {"method":"GET","uri":"/echo","args":"","host":"localhost"}

curl "http://localhost/echo?foo=bar"
# {"method":"GET","uri":"/echo","args":"foo=bar","host":"localhost"}
```

---

## Example 3: Access Phase Module

IP-based access control with custom header.

### Source Code

```c
/* ngx_http_ip_check_module.c */
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

typedef struct {
    ngx_array_t  *allowed_ips;  /* Array of ngx_cidr_t */
} ngx_http_ip_check_loc_conf_t;

static ngx_int_t ngx_http_ip_check_init(ngx_conf_t *cf);
static void *ngx_http_ip_check_create_loc_conf(ngx_conf_t *cf);
static char *ngx_http_ip_check_merge_loc_conf(ngx_conf_t *cf,
    void *parent, void *child);
static char *ngx_http_ip_check_allow(ngx_conf_t *cf, ngx_command_t *cmd,
    void *conf);
static ngx_int_t ngx_http_ip_check_handler(ngx_http_request_t *r);

static ngx_command_t ngx_http_ip_check_commands[] = {
    {
        ngx_string("ip_check_allow"),
        NGX_HTTP_LOC_CONF | NGX_CONF_TAKE1,
        ngx_http_ip_check_allow,
        NGX_HTTP_LOC_CONF_OFFSET,
        0,
        NULL
    },
    ngx_null_command
};

static ngx_http_module_t ngx_http_ip_check_module_ctx = {
    NULL,
    ngx_http_ip_check_init,
    NULL,
    NULL,
    NULL,
    NULL,
    ngx_http_ip_check_create_loc_conf,
    ngx_http_ip_check_merge_loc_conf
};

ngx_module_t ngx_http_ip_check_module = {
    NGX_MODULE_V1,
    &ngx_http_ip_check_module_ctx,
    ngx_http_ip_check_commands,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

static void *
ngx_http_ip_check_create_loc_conf(ngx_conf_t *cf)
{
    ngx_http_ip_check_loc_conf_t *conf;

    conf = ngx_pcalloc(cf->pool, sizeof(ngx_http_ip_check_loc_conf_t));
    if (conf == NULL) {
        return NULL;
    }

    return conf;
}

static char *
ngx_http_ip_check_merge_loc_conf(ngx_conf_t *cf, void *parent, void *child)
{
    ngx_http_ip_check_loc_conf_t *prev = parent;
    ngx_http_ip_check_loc_conf_t *conf = child;

    if (conf->allowed_ips == NULL) {
        conf->allowed_ips = prev->allowed_ips;
    }

    return NGX_CONF_OK;
}

static char *
ngx_http_ip_check_allow(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_ip_check_loc_conf_t *iccf = conf;
    ngx_str_t *value;
    ngx_cidr_t *cidr;

    value = cf->args->elts;

    if (iccf->allowed_ips == NULL) {
        iccf->allowed_ips = ngx_array_create(cf->pool, 4, sizeof(ngx_cidr_t));
        if (iccf->allowed_ips == NULL) {
            return NGX_CONF_ERROR;
        }
    }

    cidr = ngx_array_push(iccf->allowed_ips);
    if (cidr == NULL) {
        return NGX_CONF_ERROR;
    }

    if (ngx_ptocidr(&value[1], cidr) != NGX_OK) {
        ngx_conf_log_error(NGX_LOG_EMERG, cf, 0,
                           "invalid IP address or CIDR: \"%V\"", &value[1]);
        return NGX_CONF_ERROR;
    }

    return NGX_CONF_OK;
}

static ngx_int_t
ngx_http_ip_check_handler(ngx_http_request_t *r)
{
    ngx_http_ip_check_loc_conf_t *iccf;
    ngx_cidr_t *cidr;
    ngx_uint_t i;
    struct sockaddr_in *sin;

    iccf = ngx_http_get_module_loc_conf(r, ngx_http_ip_check_module);

    if (iccf->allowed_ips == NULL) {
        return NGX_DECLINED;  /* No restrictions */
    }

    /* Get client IP */
    if (r->connection->sockaddr->sa_family != AF_INET) {
        return NGX_DECLINED;  /* Only IPv4 for simplicity */
    }

    sin = (struct sockaddr_in *) r->connection->sockaddr;

    /* Check against allowed IPs */
    cidr = iccf->allowed_ips->elts;
    for (i = 0; i < iccf->allowed_ips->nelts; i++) {
        if ((sin->sin_addr.s_addr & cidr[i].u.in.mask)
            == cidr[i].u.in.addr)
        {
            return NGX_DECLINED;  /* Allowed, continue */
        }
    }

    ngx_log_error(NGX_LOG_WARN, r->connection->log, 0,
                  "ip_check: access denied for %V", &r->connection->addr_text);

    return NGX_HTTP_FORBIDDEN;
}

static ngx_int_t
ngx_http_ip_check_init(ngx_conf_t *cf)
{
    ngx_http_handler_pt *h;
    ngx_http_core_main_conf_t *cmcf;

    cmcf = ngx_http_conf_get_module_main_conf(cf, ngx_http_core_module);

    h = ngx_array_push(&cmcf->phases[NGX_HTTP_ACCESS_PHASE].handlers);
    if (h == NULL) {
        return NGX_ERROR;
    }

    *h = ngx_http_ip_check_handler;

    return NGX_OK;
}
```

### Usage

```nginx
location /admin {
    ip_check_allow 192.168.1.0/24;
    ip_check_allow 10.0.0.0/8;
    # ... other directives
}
```

---

## Example 4: Response Filter

Adds a custom header to all responses.

### Source Code

```c
/* ngx_http_add_header_filter_module.c */
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

static ngx_int_t ngx_http_add_header_filter_init(ngx_conf_t *cf);
static ngx_int_t ngx_http_add_header_filter(ngx_http_request_t *r);

static ngx_http_output_header_filter_pt ngx_http_next_header_filter;

static ngx_http_module_t ngx_http_add_header_filter_module_ctx = {
    NULL,
    ngx_http_add_header_filter_init,
    NULL, NULL, NULL, NULL, NULL, NULL
};

ngx_module_t ngx_http_add_header_filter_module = {
    NGX_MODULE_V1,
    &ngx_http_add_header_filter_module_ctx,
    NULL,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

static ngx_int_t
ngx_http_add_header_filter(ngx_http_request_t *r)
{
    ngx_table_elt_t *h;

    /* Only add to main request */
    if (r != r->main) {
        return ngx_http_next_header_filter(r);
    }

    /* Add custom header */
    h = ngx_list_push(&r->headers_out.headers);
    if (h == NULL) {
        return NGX_ERROR;
    }

    h->hash = 1;
    ngx_str_set(&h->key, "X-Powered-By");
    ngx_str_set(&h->value, "NGINX Custom Module");

    return ngx_http_next_header_filter(r);
}

static ngx_int_t
ngx_http_add_header_filter_init(ngx_conf_t *cf)
{
    ngx_http_next_header_filter = ngx_http_top_header_filter;
    ngx_http_top_header_filter = ngx_http_add_header_filter;

    return NGX_OK;
}
```

### Output

```bash
curl -I http://localhost/
# ...
# X-Powered-By: NGINX Custom Module
# ...
```

---

## Building Examples

```bash
# Clone example
git clone https://github.com/example/nginx-module.git

# Build with NGINX
cd nginx-1.24.0
./configure --add-module=../nginx-module
make
sudo make install

# Or as dynamic module
./configure --add-dynamic-module=../nginx-module
make modules
sudo cp objs/ngx_http_*.so /etc/nginx/modules/
```

---

## Next Steps

- Study real modules in NGINX source (`src/http/modules/`)
- Read [HTTP API](../../core-apis/http-api.md) for more patterns
- Check [3rd-party modules](../../ecosystem/3rd-party-modules.md) for inspiration
