---
title: Hardware Load Balancer Errors
description: Handling SYN-ACK-RST health checks from hardware load balancers.
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


