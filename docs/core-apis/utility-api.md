---
title: Utility API
---

# Utility API

Core utility functions for strings, memory, encoding, and conversions.

---

## Strings (`ngx_str_t`)

### Structure

```c
typedef struct {
    size_t   len;   /* String length */
    u_char  *data;  /* Pointer to data (NOT null-terminated) */
} ngx_str_t;
```

### Initialization

```c
/* Compile-time initialization */
ngx_str_t name = ngx_string("hello");

/* Runtime initialization */
ngx_str_t dynamic;
ngx_str_set(&dynamic, "world");

/* Empty/null string */
ngx_str_t empty = ngx_null_string;
ngx_str_null(&dynamic);
```

### String Operations

```c
/* Compare strings */
if (ngx_strncmp(s1.data, s2.data, s1.len) == 0) {
    /* equal */
}

/* Case-insensitive compare */
if (ngx_strncasecmp(s1.data, s2.data, s1.len) == 0) {
    /* equal ignoring case */
}

/* Check prefix */
if (ngx_strncmp(uri.data, "/api/", 5) == 0) {
    /* URI starts with /api/ */
}

/* Convert to lowercase (in-place) */
ngx_strlow(str.data, str.data, str.len);

/* Find character */
u_char *p = ngx_strlchr(str.data, str.data + str.len, '/');
if (p) {
    /* found '/' at position p */
}
```

### String Formatting

```c
u_char buf[256];
u_char *last;

/* sprintf-style formatting */
last = ngx_sprintf(buf, "Hello, %V!", &name);  /* returns end pointer */

/* Safe formatting with bounds */
last = ngx_snprintf(buf, sizeof(buf), "count: %ui, name: %V", 
                    count, &name);

/* Bounded formatting (returns end pointer) */
last = ngx_slprintf(buf, buf + sizeof(buf), "value: %d", value);
```

### Format Specifiers

| Specifier | Type | Description |
|-----------|------|-------------|
| `%V` | `ngx_str_t *` | NGINX string |
| `%v` | `ngx_variable_value_t *` | Variable value |
| `%s` | `char *` | C string |
| `%*s` | `size_t, u_char *` | Sized string |
| `%d`, `%i` | `int` | Signed integer |
| `%ui`, `%ud` | `ngx_uint_t` | Unsigned integer |
| `%l` | `long` | Long integer |
| `%ul` | `unsigned long` | Unsigned long |
| `%O` | `off_t` | File offset |
| `%z` | `ssize_t` | Signed size |
| `%uz` | `size_t` | Unsigned size |
| `%p` | `void *` | Pointer (hex) |
| `%xd`, `%xD` | `int`, `uint32_t` | Hex |
| `%M` | `ngx_msec_t` | Milliseconds |
| `%T` | `time_t` | Time |

### Duplicate String to Pool

```c
ngx_str_t *
ngx_http_copy_string(ngx_pool_t *pool, ngx_str_t *src)
{
    ngx_str_t *dst;

    dst = ngx_palloc(pool, sizeof(ngx_str_t));
    if (dst == NULL) {
        return NULL;
    }

    dst->len = src->len;
    dst->data = ngx_pstrdup(pool, src);
    if (dst->data == NULL) {
        return NULL;
    }

    return dst;
}
```

---

## Memory Operations

```c
/* Zero memory */
ngx_memzero(buf, sizeof(buf));

/* Fill with value */
ngx_memset(buf, 0xff, size);

/* Copy memory */
ngx_memcpy(dst, src, len);

/* Copy and return end pointer */
u_char *end = ngx_cpymem(dst, src, len);

/* Move (overlapping regions safe) */
ngx_memmove(dst, src, len);

/* Compare */
if (ngx_memcmp(a, b, len) == 0) {
    /* equal */
}
```

---

## Numeric Conversions

### String to Number

```c
ngx_int_t n;
ngx_str_t str = ngx_string("12345");

/* String to integer */
n = ngx_atoi(str.data, str.len);
if (n == NGX_ERROR) {
    /* Invalid number */
}

/* String to size (supports k, m suffixes) */
ssize_t size = ngx_atosz(str.data, str.len);

/* String to offset (supports k, m, g suffixes) */
off_t offset = ngx_atoof(str.data, str.len);

/* String to time (supports s, m, h, d suffixes) */
time_t t = ngx_atotm(str.data, str.len);

/* Hex string to integer */
ngx_str_t hex = ngx_string("ff");
n = ngx_hextoi(hex.data, hex.len);  /* 255 */

/* Fixed-point decimal (returns value * 10^point) */
ngx_int_t fp = ngx_atofp(str.data, str.len, 2);  /* "3.14" -> 314 */
```

### Number to String

```c
u_char buf[NGX_INT_T_LEN];
u_char *p;

/* Integer to string */
p = ngx_sprintf(buf, "%d", value);

/* Hex output */
p = ngx_sprintf(buf, "%xd", value);

/* Size with suffix */
p = ngx_sprintf(buf, "%uz", size);
```

---

## Base64 Encoding/Decoding

```c
ngx_str_t src, dst;
ngx_str_set(&src, "Hello, World!");

/* Calculate encoded length */
size_t encoded_len = ngx_base64_encoded_length(src.len);

/* Allocate and encode */
dst.data = ngx_pnalloc(pool, encoded_len);
ngx_encode_base64(&dst, &src);

/* Decode */
ngx_str_t decoded;
decoded.data = ngx_pnalloc(pool, ngx_base64_decoded_length(dst.len));
if (ngx_decode_base64(&decoded, &dst) != NGX_OK) {
    /* Invalid base64 */
}

/* URL-safe base64 */
ngx_encode_base64url(&dst, &src);
ngx_decode_base64url(&decoded, &dst);
```

---

## Hex Encoding

```c
u_char binary[] = {0xde, 0xad, 0xbe, 0xef};
u_char hex[sizeof(binary) * 2];

/* Encode to hex */
ngx_hex_dump(hex, binary, sizeof(binary));
/* hex = "deadbeef" */

/* For human-readable hex dump in logs */
static void
ngx_http_log_hex(ngx_log_t *log, u_char *data, size_t len)
{
    u_char buf[128];
    size_t i, line_len;

    for (i = 0; i < len; i += 16) {
        line_len = ngx_min(16, len - i);
        ngx_hex_dump(buf, data + i, line_len);
        ngx_log_error(NGX_LOG_DEBUG, log, 0,
                      "%04uz: %*s", i, line_len * 2, buf);
    }
}
```

---

## URL Encoding/Decoding

```c
/* Escape types */
NGX_ESCAPE_URI           /* Path segment */
NGX_ESCAPE_ARGS          /* Query string value */
NGX_ESCAPE_URI_COMPONENT /* Full URI component */
NGX_ESCAPE_HTML          /* HTML entities */

/* Calculate escaped length */
ngx_str_t src = ngx_string("hello world&foo=bar");
size_t escaped_len;

escaped_len = src.len + 2 * ngx_escape_uri(NULL, src.data, src.len,
                                           NGX_ESCAPE_ARGS);

/* Escape */
u_char *dst = ngx_pnalloc(pool, escaped_len);
u_char *p = (u_char *) ngx_escape_uri(dst, src.data, src.len,
                                      NGX_ESCAPE_ARGS);
/* dst = "hello%20world%26foo%3Dbar" */

/* Unescape */
ngx_str_t encoded = ngx_string("hello%20world");
u_char *decoded = ngx_pnalloc(pool, encoded.len);
u_char *src_ptr = encoded.data;
u_char *dst_ptr = decoded;

ngx_unescape_uri(&dst_ptr, &src_ptr, encoded.len, NGX_UNESCAPE_URI);
/* decoded = "hello world" */
```

---

## HTML/JSON Escaping

```c
/* HTML escape */
ngx_str_t html = ngx_string("<script>alert('xss')</script>");
size_t escaped_len;

escaped_len = html.len + ngx_escape_html(NULL, html.data, html.len);
u_char *escaped = ngx_pnalloc(pool, escaped_len);
ngx_escape_html(escaped, html.data, html.len);
/* escaped = "&lt;script&gt;alert('xss')&lt;/script&gt;" */

/* JSON escape */
ngx_str_t json = ngx_string("hello\nworld\"test");
size_t json_len;

json_len = json.len + ngx_escape_json(NULL, json.data, json.len);
u_char *json_escaped = ngx_pnalloc(pool, json_len);
ngx_escape_json(json_escaped, json.data, json.len);
/* json_escaped = "hello\\nworld\\\"test" */
```

---

## UTF-8 Helpers

```c
/* Validate and get length in characters */
ngx_str_t utf8 = ngx_string("Привет мир");  /* Russian "Hello world" */
size_t char_count = ngx_utf8_length(utf8.data, utf8.len);

/* Decode single codepoint */
u_char *p = utf8.data;
size_t len = utf8.len;
uint32_t codepoint;

codepoint = ngx_utf8_decode(&p, len);
if (codepoint > 0x10FFFF) {
    /* Invalid UTF-8 */
}
```

---

## Common Patterns

### Parse Key=Value

```c
static ngx_int_t
parse_key_value(ngx_str_t *input, ngx_str_t *key, ngx_str_t *value)
{
    u_char *p;

    p = ngx_strlchr(input->data, input->data + input->len, '=');
    if (p == NULL) {
        return NGX_ERROR;
    }

    key->data = input->data;
    key->len = p - input->data;

    value->data = p + 1;
    value->len = input->len - key->len - 1;

    return NGX_OK;
}
```

### Split String by Delimiter

```c
static ngx_int_t
ngx_http_split_string(ngx_pool_t *pool, ngx_str_t *input, 
                      u_char delim, ngx_array_t *parts)
{
    u_char *p, *start, *end;
    ngx_str_t *part;

    start = input->data;
    end = input->data + input->len;

    for (p = start; p <= end; p++) {
        if (p == end || *p == delim) {
            part = ngx_array_push(parts);
            if (part == NULL) {
                return NGX_ERROR;
            }

            part->data = start;
            part->len = p - start;

            start = p + 1;
        }
    }

    return NGX_OK;
}

/* Usage: split "a,b,c" into array */
ngx_array_t *parts = ngx_array_create(pool, 4, sizeof(ngx_str_t));
ngx_str_t input = ngx_string("a,b,c");
ngx_http_split_string(pool, &input, ',', parts);
```
