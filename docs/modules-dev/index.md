---
title: Module Development
---

# Module Development

This section covers **developing NGINX modules in C**, from basic concepts to advanced patterns.

---

## Why Write a Module?

NGINX modules let you:

- **Add custom directives** to nginx.conf
- **Implement new handlers** for specific locations
- **Create filters** to transform responses
- **Integrate backends** (databases, APIs, custom protocols)
- **Add variables** for use in configuration
- **Extend logging** with custom formats

---

## Module Types

### HTTP Modules

Most common type, handling HTTP requests:

```c
ngx_module_t ngx_http_mymodule_module = {
    NGX_MODULE_V1,
    &ngx_http_mymodule_module_ctx,  /* module context */
    ngx_http_mymodule_commands,      /* module directives */
    NGX_HTTP_MODULE,                 /* module type */
    /* ... */
};
```

**Examples:** proxy, fastcgi, gzip, auth_basic, rewrite

### Stream Modules

For TCP/UDP proxying (L4):

```c
ngx_module_t ngx_stream_mymodule_module = {
    NGX_MODULE_V1,
    &ngx_stream_mymodule_module_ctx,
    ngx_stream_mymodule_commands,
    NGX_STREAM_MODULE,
    /* ... */
};
```

**Examples:** stream_proxy, stream_ssl

### Mail Modules

For mail proxying (SMTP, IMAP, POP3):

```c
ngx_module_t ngx_mail_mymodule_module = {
    NGX_MODULE_V1,
    &ngx_mail_mymodule_module_ctx,
    ngx_mail_mymodule_commands,
    NGX_MAIL_MODULE,
    /* ... */
};
```

### Core Modules

Low-level functionality:

```c
ngx_module_t ngx_mycore_module = {
    NGX_MODULE_V1,
    &ngx_mycore_module_ctx,
    ngx_mycore_commands,
    NGX_CORE_MODULE,
    /* ... */
};
```

**Examples:** events, http (container), error_log

---

## Module Anatomy

Every HTTP module has these components:

```
┌─────────────────────────────────────────────────────────────┐
│                      NGINX HTTP Module                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  ngx_module_t    │    │ ngx_command_t[]  │              │
│  │  (definition)    │    │ (directives)     │              │
│  └────────┬─────────┘    └────────┬─────────┘              │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │ngx_http_module_t │    │ Configuration    │              │
│  │ (context)        │    │ Structures       │              │
│  └────────┬─────────┘    └────────┬─────────┘              │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌──────────────────────────────────────────┐              │
│  │            Handler / Filter              │              │
│  │          (request processing)            │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start: Hello World Module

### 1. Create Module File

```c
/* ngx_http_hello_module.c */
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

static char *ngx_http_hello(ngx_conf_t *cf, ngx_command_t *cmd, void *conf);
static ngx_int_t ngx_http_hello_handler(ngx_http_request_t *r);

/* Directive */
static ngx_command_t ngx_http_hello_commands[] = {
    {
        ngx_string("hello"),
        NGX_HTTP_LOC_CONF | NGX_CONF_NOARGS,
        ngx_http_hello,
        0, 0, NULL
    },
    ngx_null_command
};

/* Module context */
static ngx_http_module_t ngx_http_hello_module_ctx = {
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
};

/* Module definition */
ngx_module_t ngx_http_hello_module = {
    NGX_MODULE_V1,
    &ngx_http_hello_module_ctx,
    ngx_http_hello_commands,
    NGX_HTTP_MODULE,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NGX_MODULE_V1_PADDING
};

/* Directive handler */
static char *
ngx_http_hello(ngx_conf_t *cf, ngx_command_t *cmd, void *conf)
{
    ngx_http_core_loc_conf_t *clcf;
    clcf = ngx_http_conf_get_module_loc_conf(cf, ngx_http_core_module);
    clcf->handler = ngx_http_hello_handler;
    return NGX_CONF_OK;
}

/* Request handler */
static ngx_int_t
ngx_http_hello_handler(ngx_http_request_t *r)
{
    ngx_buf_t *b;
    ngx_chain_t out;
    static u_char hello[] = "Hello, World!\n";

    r->headers_out.status = NGX_HTTP_OK;
    r->headers_out.content_length_n = sizeof(hello) - 1;
    ngx_str_set(&r->headers_out.content_type, "text/plain");

    ngx_http_send_header(r);

    b = ngx_pcalloc(r->pool, sizeof(ngx_buf_t));
    b->pos = hello;
    b->last = hello + sizeof(hello) - 1;
    b->memory = 1;
    b->last_buf = 1;

    out.buf = b;
    out.next = NULL;

    return ngx_http_output_filter(r, &out);
}
```

### 2. Create config File

```
# config
ngx_addon_name=ngx_http_hello_module
HTTP_MODULES="$HTTP_MODULES ngx_http_hello_module"
NGX_ADDON_SRCS="$NGX_ADDON_SRCS $ngx_addon_dir/ngx_http_hello_module.c"
```

### 3. Build and Install

```bash
# Configure with module
./configure --add-module=/path/to/hello_module

# Build
make

# Install
sudo make install
```

### 4. Configure and Test

```nginx
location /hello {
    hello;
}
```

```bash
curl http://localhost/hello
# Output: Hello, World!
```

---

## Learning Path

### Beginner

1. [Compiling NGINX & Modules](compiling.md) - Build process
2. [Configuration Directives](configuration.md) - Define directives
3. Read existing simple modules (e.g., `ngx_http_empty_gif_module.c`)

### Intermediate

4. [Core APIs Overview](../core-apis/index.md) - Key structures
5. [HTTP API](../core-apis/http-api.md) - Request handling
6. [Memory Management](../core-apis/memory-api.md) - Pools and allocation

### Advanced

7. [Event API](../core-apis/event-api.md) - Async operations
8. [Variables API](../core-apis/variables-api.md) - Custom variables
9. Write filters and upstream modules

---

## Module Examples

| Module | Type | Complexity | Description |
|--------|------|------------|-------------|
| `ngx_http_empty_gif_module` | Handler | Simple | Returns 1x1 GIF |
| `ngx_http_stub_status_module` | Handler | Simple | Status page |
| `ngx_http_access_module` | Access | Simple | IP allow/deny |
| `ngx_http_auth_basic_module` | Access | Medium | Basic auth |
| `ngx_http_rewrite_module` | Rewrite | Medium | URL rewriting |
| `ngx_http_gzip_filter_module` | Filter | Medium | Compression |
| `ngx_http_proxy_module` | Upstream | Complex | HTTP proxy |
| `ngx_http_lua_module` | Embedded | Complex | Lua scripting |

---

## Development Environment

### Prerequisites

```bash
# Debian/Ubuntu
apt install build-essential libpcre3-dev zlib1g-dev libssl-dev

# RHEL/CentOS
yum groupinstall "Development Tools"
yum install pcre-devel zlib-devel openssl-devel

# macOS
xcode-select --install
brew install pcre zlib openssl
```

### Debugging Build

```bash
./configure --with-debug \
            --with-cc-opt="-O0 -g" \
            --add-module=/path/to/module

make
```

### IDE Setup

For VSCode, create `.vscode/c_cpp_properties.json`:

```json
{
    "configurations": [{
        "name": "NGINX",
        "includePath": [
            "${workspaceFolder}/**",
            "/path/to/nginx/src/core",
            "/path/to/nginx/src/event",
            "/path/to/nginx/src/http",
            "/path/to/nginx/src/os/unix",
            "/path/to/nginx/objs"
        ],
        "defines": [],
        "compilerPath": "/usr/bin/gcc",
        "cStandard": "c11"
    }],
    "version": 4
}
```

---

## Resources

### Official

- [NGINX Development Guide](https://nginx.org/en/docs/dev/development_guide.html)
- [NGINX Source Code](https://github.com/nginx/nginx)

### Pre-Built Modules

- [NGINX Extras](https://nginx-extras.getpagespeed.com/modules/) - 100+ pre-built modules for RHEL/CentOS
- [APT NGINX Extras](https://apt-nginx-extras.getpagespeed.com/apt-setup/) - Modules for Debian/Ubuntu

### Community

- [Emiller's Guide to NGINX Module Development](https://www.evanmiller.org/nginx-modules-guide.html)
- [NGINX 3rd Party Modules](../ecosystem/3rd-party-modules.md)

### Books

- *NGINX Module Extension* by Usama Dar
- *Nginx Essentials* by Valery Kholodkov

---

## Next Steps

1. **[Compiling NGINX](compiling.md)** - Learn the build system
2. **[Configuration Directives](configuration.md)** - Define your first directive
3. **[Working Examples](examples/index.md)** - Study complete modules
