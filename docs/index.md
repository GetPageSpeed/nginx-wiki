---
title: NGINX Wiki
---

<div class="hero" markdown="1">

# NGINX Wiki

Community documentation for **NGINX configuration, architecture, and module development**.

It focuses on how NGINX really works under the hood: the event loop and
process model, the C APIs behind HTTP and upstreams, and how configuration
maps onto those internals.

<div class="hero-actions" markdown="1">

[Explore architecture →](architecture/index.md){ .md-button .md-button--primary }
[Browse core APIs →](core-apis/index.md){ .md-button }
[Start with module development →](modules-dev/index.md){ .md-button }

</div>

</div>

## What you'll find here

<div class="feature-grid" markdown="1">

<div class="feature-card" markdown="1">

### :material-dns-outline: Architecture

End-to-end overview of the **master/worker** process model, event loop,
timers, and HTTP request lifecycle.

[Read the architecture guide](architecture/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-code-braces: Core C APIs

Reference documentation for core types like `ngx_http_request_t`,
`ngx_module_t`, memory pools, buffers, logging, and configuration helpers.

[Browse core APIs](core-apis/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-puzzle-outline: Module development

Guidance for building and debugging modules: compilation options,
configuration structures, and worked examples of filters and handlers.

[Go to module development](modules-dev/index.md)

</div>

<div class="feature-card" markdown="1">

### :material-share-variant-outline: Ecosystem & community

Curated links to important **3rd-party modules**, talks, and learning
resources.

[See ecosystem & community](ecosystem/3rd-party-modules.md)

</div>

</div>
