---
title: Source Code Tricks
description: Handy bash commands for exploring the NGINX source.
---

# Source Code Tricks

Useful commands for exploring the NGINX source code.

## All Directives in Server Context

```bash
find src/ -type f -name "*.c" -exec grep -B1 NGX_HTTP_SRV_CONF {} \; | \
    grep ngx_string | cut -d\" -f2
```

## All Variables in HTTP Context

```bash
find src/ -type f -name "*.c" -exec grep -B2 NGX_HTTP_VAR {} \; | \
    grep ngx_string | cut -d\" -f2
```

## All Module Names

```bash
grep -r "ngx_module_t" src/ --include="*.c" | grep "ngx_.*_module ="
```

## Search for Directive Handler

```bash
grep -r "ngx_command_t" src/ --include="*.c" -A5 | grep "directive_name"
```


