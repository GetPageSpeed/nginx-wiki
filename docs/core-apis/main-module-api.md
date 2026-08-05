---
title: NGINX Main Module API - Core Types and Structures Reference
description: Reference guide for NGINX core types including ngx_module_t, ngx_cycle_t, ngx_connection_t, and module context structures for HTTP and mail.
keywords: nginx main module api, ngx_module_t, ngx_cycle_t, ngx_connection_t, nginx core types, nginx module context
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - core api
  - module types
  - ngx_module_t
  - ngx_cycle_t
---

# Main module API

This page summarises core types and structures that are central to NGINX
itself and widely referenced from modules.

The content here is adapted from the `main.rst` Module API documentation in
the historical NGINX Wiki.

## Basic scalar types

These are convenience typedefs used throughout the NGINX core and modules:

- `ngx_pid_t`: integer type used to store process IDs
- `ngx_cycle_t`: *event cycle object* representing the current runtime state
- `ngx_uint_t`: alias for `unsigned int`
- `ngx_int_t`: alias for `int`
- `ngx_flag_t`: boolean flag type (typically `0` or `1`)
- `ngx_msec_t`: millisecond count, alias for `ngx_uint_t`
- `ngx_file_t`: describes an open file descriptor and its metadata
- `ngx_peer_connection_t`: represents an upstream peer connection
- `size_t`, `off_t`, `time_t`, `in_port_t`, `va_list`, `ssize_t`,
  `uintptr_t`, `uint32_t`: standard C types used with conventional meanings

## `ngx_module_t`

`ngx_module_t` is the central structure used to define a module.

Key members (simplified):

- `ctx`: module‑specific context pointer, usually pointing to:
  - `ngx_core_module_t` for core modules
  - `ngx_http_module_t` for HTTP modules
  - `ngx_mail_module_t` for mail modules
- `commands`: pointer to an `ngx_command_t` array defining configuration
  directives for the module
- `type`: module type, set using one of:
  - `NGX_CORE_MODULE`
  - `NGX_HTTP_MODULE`
  - `NGX_EVENT_MODULE`
  - `NGX_MAIL_MODULE`
  - `NGX_STREAM_MODULE`
- Lifecycle hooks:
  - `init_master(ngx_log_t *log)`
  - `init_module(ngx_cycle_t *cycle)`
  - `init_process(ngx_cycle_t *cycle)`
  - `init_thread(ngx_cycle_t *cycle)`
  - `exit_thread(ngx_cycle_t *cycle)`
  - `exit_process(ngx_cycle_t *cycle)`
  - `exit_master(ngx_cycle_t *cycle)`

The `NGX_MODULE_V1` and `NGX_MODULE_V1_PADDING` macros are used for the header
and footer of the structure respectively.

Example (from the original docs):

```c
ngx_module_t ngx_http_my_module = {
    NGX_MODULE_V1,
    &ngx_http_my_module_ctx,      /* module context */
    ngx_http_my_module_commands,  /* module directives */
    NGX_HTTP_MODULE,              /* module type */
    NULL,                         /* init master */
    NULL,                         /* init module */
    NULL,                         /* init process */
    NULL,                         /* init thread */
    NULL,                         /* exit thread */
    NULL,                         /* exit process */
    NULL,                         /* exit master */
    NGX_MODULE_V1_PADDING
};
```

## `ngx_core_module_t`

Defines the **core context** for a module:

- `name`: module name (`ngx_str_t`)
- `create_conf(cycle)`: allocates and initialises configuration data
- `init_conf(cycle)`: finalises configuration based on parsed directives

## `ngx_http_module_t`

Defines the **HTTP module context**, used by all HTTP modules:

- `preconfiguration(cf)`: called before parsing HTTP configuration
- `postconfiguration(cf)`: called after configuration is parsed
- `create_main_conf(cf)` / `init_main_conf(cf, conf)`
- `create_srv_conf(cf)` / `merge_srv_conf(cf, prev, conf)`
- `create_loc_conf(cf)` / `merge_loc_conf(cf, prev, conf)`

These callbacks control allocation and merging of configuration structures at
the `http`, `server`, and `location` levels.

## `ngx_mail_module_t`

Defines the **mail module context**:

- `protocol`: pointer to an `ngx_mail_protocol_t` structure
- `create_main_conf(cf)` / `init_main_conf(cf, conf)`
- `create_srv_conf(cf)` / `merge_srv_conf(cf, prev, conf)`

## `ngx_connection_t`

Represents a single connection (for example a client TCP connection).

For module authors, the most commonly referenced member is:

- `log`: pointer to an `ngx_log_t` used for logging in the context of the
  connection.

