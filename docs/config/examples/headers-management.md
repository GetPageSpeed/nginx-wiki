---
title: NGINX Module Development HTTP Headers Management
description: Manage HTTP headers in NGINX C modules with headers_in, headers_out structures, hash lookups, and custom header manipulation code.
keywords: nginx headers, nginx module development, nginx headers_in, nginx headers_out, nginx c module, nginx header api
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - module development
  - headers
  - c programming
  - api
---

# Headers Management

HTTP headers in NGINX are split into input (`headers_in`) and output (`headers_out`) structures.

## Getting Header Values

### Brute Force Search

```c
static ngx_table_elt_t *
search_headers_in(ngx_http_request_t *r, u_char *name, size_t len) {
    ngx_list_part_t *part;
    ngx_table_elt_t *h;
    ngx_uint_t i;

    part = &r->headers_in.headers.part;
    h = part->elts;

    for (i = 0; ; i++) {
        if (i >= part->nelts) {
            if (part->next == NULL) {
                break;
            }
            part = part->next;
            h = part->elts;
            i = 0;
        }

        if (len != h[i].key.len || 
            ngx_strcasecmp(name, h[i].key.data) != 0) {
            continue;
        }

        return &h[i];
    }

    return NULL;
}
```

### Quick Hash Search

```c
ngx_table_elt_t *
search_hashed_headers_in(ngx_http_request_t *r, u_char *name, size_t len) {
    ngx_http_core_main_conf_t *cmcf;
    ngx_http_header_t *hh;
    u_char *lowcase_key;
    ngx_uint_t i, hash;

    lowcase_key = ngx_palloc(r->pool, len);
    if (lowcase_key == NULL) {
        return NULL;
    }

    hash = 0;
    for (i = 0; i < len; i++) {
        lowcase_key[i] = ngx_tolower(name[i]);
        hash = ngx_hash(hash, lowcase_key[i]);
    }

    cmcf = ngx_http_get_module_main_conf(r, ngx_http_core_module);
    hh = ngx_hash_find(&cmcf->headers_in_hash, hash, lowcase_key, len);

    if (hh == NULL || hh->offset == 0) {
        return NULL;
    }

    return *((ngx_table_elt_t **) ((char *) &r->headers_in + hh->offset));
}
```

### Direct Field Access (Fastest)

```c
ngx_table_elt_t *
get_host_from_headers_in(ngx_http_request_t *r) {
    return r->headers_in.host;
}

off_t
get_content_length_n_from_headers_in(ngx_http_request_t *r) {
    return r->headers_in.content_length_n;  // -1 if not set
}
```

## Setting Headers

### Setting Content-Length

```c
ngx_int_t
set_content_length_n_in_headers_out(ngx_http_request_t *r, 
                                     ngx_str_t *length, 
                                     off_t length_n) {
    ngx_table_elt_t *h;

    h = r->headers_out.content_length;
    if (h == NULL) {
        h = ngx_list_push(&r->headers_out.headers);
        if (h == NULL) {
            return NGX_ERROR;
        }

        h->key.data = (u_char *) "Content-Length";
        h->key.len = sizeof("Content-Length") - 1;
        r->headers_out.content_length = h;
    }

    h->value = *length;
    h->hash = 1;  // Mark as active
    r->headers_out.content_length_n = length_n;

    return NGX_OK;
}
```

### Setting Custom Headers

```c
ngx_int_t
set_custom_header_in_headers_out(ngx_http_request_t *r, 
                                  ngx_str_t *key, 
                                  ngx_str_t *value) {
    ngx_table_elt_t *h;

    h = ngx_list_push(&r->headers_out.headers);
    if (h == NULL) {
        return NGX_ERROR;
    }

    h->key = *key;
    h->value = *value;
    h->hash = 1;

    return NGX_OK;
}
```

!!! warning "proxy_pass Headers"
    When using `proxy_pass`, header keys must be lowercased:
    ```c
    header->key = (u_char *) "X-Custom-Header";
    header->lowcase_key = (u_char *) "x-custom-header";
    ```


