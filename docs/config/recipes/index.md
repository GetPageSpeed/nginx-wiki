---
title: NGINX Application Configuration Recipes
description: Ready-to-use NGINX configuration recipes for popular web applications, frameworks, CMS, and e-commerce platforms.
keywords: nginx, configuration, recipes, web applications, php, python, ruby, java, cms, frameworks
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - configuration
  - recipes
  - web applications
  - php frameworks
  - cms
  - e-commerce
---

# Application Recipes

Ready-to-use NGINX configurations for popular web applications and frameworks.

---

## PHP Frameworks & CMS

| Application | Description |
|-------------|-------------|
| [PHP-FPM](php-fpm.md) | PHP FastCGI Process Manager setup |
| [WordPress](wordpress.md) | Blog & CMS platform with multisite support |
| [Drupal](drupal.md) | Content management framework |
| [Symfony](symfony.md) | PHP framework (versions 2.x - 6.x) |
| [CodeIgniter](codeigniter.md) | Lightweight PHP framework |
| [Yii](yii.md) | High-performance PHP framework |
| [Zend Framework](zend.md) | Enterprise PHP framework |
| [MediaWiki](mediawiki.md) | Wiki platform (powers Wikipedia) |

---

## E-commerce

| Application | Description |
|-------------|-------------|
| [Shopware](shopware.md) | Open-source e-commerce platform |
| [osCommerce](oscommerce.md) | E-commerce with SEO-friendly URLs |

---

## Forums & Community

| Application | Description |
|-------------|-------------|
| [XenForo](xenforo.md) | Modern forum software |
| [MyBB](mybb.md) | Free forum software |

---

## Wikis & Documentation

| Application | Description |
|-------------|-------------|
| [DokuWiki](dokuwiki.md) | Simple wiki without database |
| [PmWiki](pmwiki.md) | Wiki for collaborative websites |
| [MoinMoin](moinmoin.md) | Python-based wiki with uWSGI |

---

## Project Management & Analytics

| Application | Description |
|-------------|-------------|
| [Redmine](redmine.md) | Ruby project management |
| [Matomo](matomo.md) | Web analytics (formerly Piwik) |
| [b2evolution](b2evolution.md) | Blog/CMS with forums |

---

## Python Frameworks

| Application | Description |
|-------------|-------------|
| [Django](django.md) | Python web framework with FastCGI/Gunicorn |
| [Pylons](pylons.md) | Python web framework with Flup |

---

## Ruby Applications

| Application | Description |
|-------------|-------------|
| [Ruby (Unicorn/Puma)](ruby.md) | Ruby app servers via Unix socket |

---

## Java/JVM

| Application | Description |
|-------------|-------------|
| [Java servers](java-servers.md) | Jetty, Tomcat, GlassFish as backends |

---

## Common Patterns

Most PHP applications follow similar patterns:

```nginx
server {
    server_name example.com;
    root /var/www/app;
    index index.php;

    # Static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires max;
        log_not_found off;
    }

    # Route requests to front controller
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # PHP handling
    location ~ \.php$ {
        try_files $uri =404;
        include fastcgi_params;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    # Block hidden files
    location ~ /\. {
        deny all;
    }
}
```
