---
title: NGINX Handling Hardware Load Balancer Health Check Errors
description: Fix NGINX 400 errors from hardware load balancers like Cisco CSS and F5 BigIP SYN-ACK-RST health checks using geo module.
keywords: nginx hardware load balancer, nginx f5, nginx cisco css, nginx 400 error, nginx health check, nginx geo module
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - load balancer
  - health check
  - f5
  - cisco
---

# Hardware Load Balancer Errors

Some hardware load balancers (Cisco CSS, F5 BigIP) test backend readiness with `SYN-ACK-RST`, causing 400 errors in NGINX.

## Solution

Use the GEO module to suppress logging for load balancer IPs:

```nginx
http {
    geo $lb {
        default     0;
        10.1.1.1/32 1;   # Load balancer IPs
        10.1.1.2/32 1;
    }

    server {
        access_log /path/to/log;
        error_page 400 /400;

        location = /400 {
            if ($lb) {
                access_log off;
            }
            return 400;
        }
    }
}
```


