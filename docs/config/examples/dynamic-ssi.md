---
title: NGINX Dynamic Content with Server Side Includes (SSI)
description: Create dynamic web pages using NGINX SSI without a framework. Include templates, variables, and conditional content server-side.
keywords: nginx ssi, nginx server side includes, nginx dynamic content, nginx templates, nginx include, ssi directive
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - ssi
  - server side includes
  - dynamic content
  - templates
---

# Dynamic SSI

Create "dynamic" content without a web framework using Server Side Includes.

## Configuration

```nginx
http {
    include mime.types;
    default_type application/octet-stream;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 10;
    gzip on;

    server {
        server_name localhost;
        charset utf-8;
        access_log /var/log/nginx/access.log;
        root /var/www;

        location = / {
            rewrite ^ /home redirect;
        }

        location / {
            ssi on;
            set $inc $request_uri;

            if (!-f $request_filename) {
                rewrite ^ /index.html last;
            }

            if (!-f $document_root$inc.html) {
                return 404;
            }
        }
    }
}
```

## Template (index.html)

```html
<html>
<body>
    <!--# include file="$inc.html" -->
</body>
</html>
```

## How It Works

1. Request to `/home` → includes `home.html` into `index.html`
2. Request to `/about` → includes `about.html` into `index.html`
3. Common headers/footers stay in `index.html`

!!! note
    This assumes `home.html` exists as the default page.


