---
title: Forwarded Header (RFC 7239)
description: NGINX configuration for deploying the standardized Forwarded header.
---

# Forwarded Header (RFC 7239)

Traditionally, HTTP reverse proxies use non-standard headers:

```
X-Forwarded-For: 12.34.56.78, 23.45.67.89
X-Real-IP: 12.34.56.78
X-Forwarded-Host: example.com
X-Forwarded-Proto: https
```

[RFC 7239](https://tools.ietf.org/html/rfc7239) standardizes the `Forwarded` header:

```
Forwarded: for=12.34.56.78;host=example.com;proto=https, for=23.45.67.89
```

## Benefits

The `Forwarded` header is **extensible**. For example, your trusted proxy can include a secret token:

```
Forwarded: for=12.34.56.78, for=23.45.67.89;secret=egah2CGj55fSJFs, for=10.1.2.3
```

---

## NGINX Configuration

NGINX doesn't provide a built-in `$proxy_add_forwarded` variable, but you can emulate it:

```nginx
map $remote_addr $proxy_forwarded_elem {
    # IPv4 addresses can be sent as-is
    ~^[0-9.]+$          "for=$remote_addr";

    # IPv6 addresses need to be bracketed and quoted
    ~^[0-9A-Fa-f:.]+$   "for=\"[$remote_addr]\"";

    # Unix domain socket names cannot be represented in RFC 7239 syntax
    default             "for=unknown";
}

map $http_forwarded $proxy_add_forwarded {
    # If the incoming Forwarded header is syntactically valid, append to it
    "~^(,[ \\t]*)*([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?(;([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?)*([ \\t]*,([ \\t]*([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?(;([!#$%&'*+.^_`|~0-9A-Za-z-]+=([!#$%&'*+.^_`|~0-9A-Za-z-]+|\"([\\t \\x21\\x23-\\x5B\\x5D-\\x7E\\x80-\\xFF]|\\\\[\\t \\x21-\\x7E\\x80-\\xFF])*\"))?)*)?)*$" "$http_forwarded, $proxy_forwarded_elem";

    # Otherwise, replace it
    default "$proxy_forwarded_elem";
}
```

Then in your `proxy_pass` block:

```nginx
proxy_set_header Forwarded $proxy_add_forwarded;
```

You can also append extra parameters:

```nginx
proxy_set_header Forwarded "$proxy_add_forwarded;proto=$scheme";
```

!!! warning "Multiple Headers Limitation"
    This solution **does not support** multiple incoming `Forwarded` headers. Unlike `$proxy_add_x_forwarded_for`, it won't correctly join:
    
    ```
    Forwarded: for=1.2.3.4
    Forwarded: for=5.6.7.8
    ```

---

## Dealing with Invalid Headers

The complex regex above validates the `Forwarded` header syntax. Without validation, an attacker could send:

```
Forwarded: for=injected;by="
```

Which would produce:

```
Forwarded: for=injected;by=", for=real
```

If you trust your upstream to handle malformed headers, use a simpler config:

```nginx
map $http_forwarded $proxy_add_forwarded {
    ""      "$proxy_forwarded_elem";
    default "$http_forwarded, $proxy_forwarded_elem";
}
```

---

## Coexistence with X-Forwarded-*

You can either pass both headers:

```nginx
proxy_set_header Forwarded $proxy_add_forwarded;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

Or remove legacy headers to avoid confusion:

```nginx
proxy_set_header Forwarded $proxy_add_forwarded;
proxy_set_header X-Forwarded-For "";
```


