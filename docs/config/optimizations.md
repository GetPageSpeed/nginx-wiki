---
title: Optimizations
description: This page describes ways to optimize your NGINX configurations to improve your request processing speed.
---

# Optimizations

NGINX is known for its high performance and low resource usage. This page focuses on configuration-level optimizations that relate directly to internal design.

---

## Hash Tables

To assist with the rapid processing of requests, NGINX uses hash tables.

During startup and with each reconfiguration, NGINX selects the smallest possible size for the hash tables, taking into account the size of buckets where keys with coinciding hashed values fall.

Selection is conducted until the size of table exceeds the `hash_max_size` parameter. For the majority of hashes there are directives which make it possible to change these parameters.

For example, the hash with the names of servers is controlled by:

- `server_names_hash_max_size`
- `server_names_hash_bucket_size`

### Hash Bucket Size and CPU Cache

The `hash_bucket_size` parameter is always equalized to the size that is a multiple of the processor cache line size. This makes it possible to accelerate key lookup in the hash on processors by decreasing the number of memory accesses.

If `hash_bucket_size` is equal to the size of one processor cache line, then during key lookup the number of memory accesses in the worst case will be equal to two:

1. First to determine the address of the bucket
2. Second to search for the key inside the bucket

!!! tip
    If NGINX reports the need for increasing `hash_max_size` or `hash_bucket_size`, it is first necessary to increase `hash_max_size`.

---

## Event Models

NGINX supports the following methods of treating connections, which can be assigned by the `use` directive in the `events` block:

| Method | Description |
|--------|-------------|
| **select** | Standard method. Compiled by default if the current platform does not have a more effective method. Enable/disable with `--with-select_module` and `--without-select_module`. |
| **poll** | Standard method. Compiled by default if the current platform does not have a more effective method. Enable/disable with `--with-poll_module` and `--without-poll_module`. |
| **kqueue** | Effective method used on FreeBSD 4.1+, OpenBSD 2.9+, NetBSD 2.0, and macOS. |
| **epoll** | Effective method used on Linux 2.6+. |
| **/dev/poll** | Effective method used on Solaris 7 11/99+, HP/UX 11.22+, IRIX 6.5.15+, and Tru64 UNIX 5.1A+. |

### Choosing the Right Event Model

NGINX automatically selects the most efficient method available for your platform. You generally don't need to specify this manually unless you're debugging or have specific requirements.

```nginx
events {
    use epoll;  # Linux
    # use kqueue;  # FreeBSD/macOS
}
```

---

## Worker Processes

### Worker Count

Set the number of worker processes. The optimal value depends on many factors including (but not limited to) the number of CPU cores, the number of hard disk drives that store data, and load pattern.

When in doubt, setting it to the number of available CPU cores is a good start:

```nginx
worker_processes auto;
```

Or explicitly:

```nginx
worker_processes 4;
```

### Worker Connections

The maximum number of simultaneous connections that can be opened by a worker process:

```nginx
events {
    worker_connections 4096;
}
```

Keep in mind that this number includes all connections (e.g. connections with proxied servers), not only connections with clients. The total number of simultaneous connections cannot exceed the current limit on the maximum number of open files.

### CPU Affinity

Bind worker processes to specific CPU cores:

```nginx
worker_processes 4;
worker_cpu_affinity 0001 0010 0100 1000;
```

Or let NGINX handle it automatically:

```nginx
worker_processes auto;
worker_cpu_affinity auto;
```

---

## File Descriptors

### Worker File Limit

Changes the limit on the maximum number of open files for worker processes:

```nginx
worker_rlimit_nofile 65535;
```

### Open File Cache

Cache information about open file descriptors, their sizes, and modification times:

```nginx
open_file_cache max=10000 inactive=20s;
open_file_cache_valid 30s;
open_file_cache_min_uses 2;
open_file_cache_errors on;
```

---

## Sendfile and TCP Options

### Sendfile

Enables the use of `sendfile()` to transfer data between file descriptors directly in kernel space:

```nginx
sendfile on;
```

### TCP Nopush

Enables or disables the `TCP_NOPUSH` socket option on FreeBSD or the `TCP_CORK` socket option on Linux:

```nginx
tcp_nopush on;
```

This is only enabled when `sendfile` is used. It causes nginx to attempt to send its HTTP response head in one packet.

### TCP Nodelay

Enables or disables the `TCP_NODELAY` option. The option is enabled when a connection is transitioned into the keep-alive state:

```nginx
tcp_nodelay on;
```

---

## Compression

Enable gzip compression to reduce the amount of data transferred:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1000;
gzip_proxied any;
gzip_types text/plain text/css text/xml application/json application/javascript;
gzip_comp_level 6;
```

!!! warning
    Don't over-compress. Higher compression levels use more CPU. Level 6 is usually a good balance.

---

## Buffers

### Client Body Buffer

Sets buffer size for reading client request body:

```nginx
client_body_buffer_size 16k;
```

### Proxy Buffers

Sets the number and size of buffers used for reading a response from the proxied server:

```nginx
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 16k;
proxy_busy_buffers_size 24k;
```

