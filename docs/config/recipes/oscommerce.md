---
title: NGINX osCommerce Configuration Guide
description: Configure NGINX for osCommerce e-commerce platform with SEO-friendly URLs, URL rewriting, and security hardening.
keywords: nginx, oscommerce, e-commerce, ecommerce, seo urls, online store, php, shopping cart
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - oscommerce
  - e-commerce
  - php
  - seo urls
---

# osCommerce

## Configuration

```nginx
server {
    server_name www.domain.com;
    server_name_in_redirect off;

    root /var/www/www.domain.com/catalog;
    access_log /var/www/www.domain.com/logs/access.log;
    error_log /var/www/www.domain.com/logs/error.log;

    # Static content caching
    location / { expires max; }

    # Block access to sensitive directories
    location ~ ^/includes/.*\.php$ { return 403; }
    location ~ ^/admin/includes/.*\.php$ { return 403; }
    location ^~ /admin/backups { return 403; }
    location ^~ /download { return 403; }

    # osCommerce SEO rewrites
    location ~ -p-(?<id>[0-9]+)\.html$ {
        rewrite ^ /product_info.php?products_id=$id;
    }
    location ~ -c-(?<id>[0-9_]+)\.html$ {
        rewrite ^ /index.php?cPath=$id;
    }
    location ~ -m-(?<id>[0-9]+)\.html$ {
        rewrite ^ /index.php?manufacturers_id=$id;
    }
    location ~ -pi-(?<id>[0-9]+)\.html$ {
        rewrite ^ /popup_image.php?pID=$id;
    }
    location ~ -pr-(?<id>[0-9]+)\.html$ {
        rewrite ^ /product_reviews.php?products_id=$id;
    }
    location ~ -pri-(?<id>[0-9]+)\.html$ {
        rewrite ^ /product_reviews_info.php?products_id=$id;
    }

    # Articles contribution
    location ~ -t-(?<id>[0-9_]+)\.html$ {
        rewrite ^ /articles.php?tPath=$id;
    }
    location ~ -a-(?<id>[0-9]+)\.html$ {
        rewrite ^ /article_info.php?articles_id=$id;
    }

    # Information pages
    location ~ -i-(?<id>[0-9]+)\.html$ {
        rewrite ^ /information.php?info_id=$id;
    }

    # PHP handling
    location ~ \.php$ {
        if (!-f $request_filename) { return 404; }
        include fastcgi_params;
        fastcgi_param HTTP_PROXY "";
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param REDIRECT_STATUS 200;
        fastcgi_pass 127.0.0.1:9000;
    }
}
```
