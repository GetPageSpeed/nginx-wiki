---
title: Managing Request Headers
description: How to read and set HTTP headers in NGINX module development.
---

# Managing Request Headers

This guide covers the internal structures and functions for handling HTTP headers in NGINX module development.

---

## Header Storage Architecture

NGINX stores headers in two main structures:

| Structure | Purpose |
|-----------|---------|
| `headers_in` | Input request headers from client |
| `headers_out` | Output headers for response |

Both structures live in `ngx_http_request_t`. There is no separate "response" entity—all data is stored in a single request structure.

---

## HTTP Header Flexibility

HTTP headers are flexible but complex:

- Single header with one value
- Multiple headers with the same name
- One header split across multiple lines

NGINX handles this complexity with optimized storage:

1. **Known headers** → Direct pointer in `headers_in`/`headers_out`
2. **Multi-value headers** → Arrays (e.g., Cookies, Cache-Control)
3. **Numeric headers** → Pre-parsed numeric field (e.g., `content_length_n`)
4. **Unknown headers** → Plain list (`headers.headers`)

---

## Getting Header Values

### Method 1: Brute Force Search

Search through all headers by name:

```c
static ngx_table_elt_t *
search_headers_in(ngx_http_request_t *r, u_char *name, size_t len) {
    ngx_list_part_t  *part;
    ngx_table_elt_t  *h;
    ngx_uint_t        i;

    part = &r->headers_in.headers.part;
    h = part->elts;

    for (i = 0; /* void */ ; i++) {
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

### Method 2: Hash Lookup (Known Headers)

Fast lookup for headers NGINX knows about:

```c
ngx_table_elt_t *
search_hashed_headers_in(ngx_http_request_t *r, u_char *name, size_t len) {
    ngx_http_core_main_conf_t  *cmcf;
    ngx_http_header_t          *hh;
    u_char                     *lowcase_key;
    ngx_uint_t                  i, hash;

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

### Method 3: Direct Field Access (Fastest)

For known headers, access the field directly:

```c
ngx_table_elt_t *
get_host_from_headers_in(ngx_http_request_t *r) {
    return r->headers_in.host;  // NULL if not present
}
```

### Method 4: Pre-Parsed Numeric Values (Fastest)

For numeric headers:

```c
off_t
get_content_length_n_from_headers_in(ngx_http_request_t *r) {
    return r->headers_in.content_length_n;  // -1 if not set
}
```

---

## Setting Header Values

### Setting Known Headers (e.g., Content-Length)

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
    h->hash = 1;  // Mark as active (required!)

    r->headers_out.content_length_n = length_n;

    return NGX_OK;
}
```

### Setting Custom (Unknown) Headers

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
    h->hash = 1;  // Mark as active

    return NGX_OK;
}
```

!!! warning "`h->hash = 1`"
    This tells `ngx_http_header_module` to include the header in the response. Without it, the header is ignored.

---

## Proxy Pass Considerations

When using `proxy_pass` with custom headers, you **must** set the lowercased key:

```c
header->key = (u_char *) "X-Custom-Header";
header->lowcase_key = (u_char *) "x-custom-header";
```

!!! danger "Crash Warning"
    The HTTP proxy module expects lowercased keys. Without `lowcase_key`, the module will crash on subrequests.

---

## Common Known Headers

### headers_in

| Field | Header |
|-------|--------|
| `host` | Host |
| `connection` | Connection |
| `user_agent` | User-Agent |
| `referer` | Referer |
| `content_length` | Content-Length |
| `content_type` | Content-Type |
| `authorization` | Authorization |
| `cookies` | Cookie (array) |

### headers_out

| Field | Header |
|-------|--------|
| `status` | HTTP status code |
| `content_length` | Content-Length |
| `content_type` | Content-Type |
| `location` | Location |
| `last_modified` | Last-Modified |
| `etag` | ETag |

---

## References

- [headers_in source](https://github.com/nginx/nginx/blob/master/src/http/ngx_http_request.h#L162)
- [headers_out source](https://github.com/nginx/nginx/blob/master/src/http/ngx_http_request.h#L227)
- [Known headers_in list](https://github.com/nginx/nginx/blob/master/src/http/ngx_http_request.c#L80)


