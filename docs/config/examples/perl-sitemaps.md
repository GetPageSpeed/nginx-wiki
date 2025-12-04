---
title: Embedded Perl Sitemaps Proxy
description: Dynamic sitemap proxy using NGINX embedded Perl.
---

# Embedded Perl Sitemaps Proxy

Serve sitemaps for multiple domains from a central server.

## NGINX Configuration

```nginx
http {
    perl_modules lib;
    perl_require Sitemap.pm;

    server {
        listen 8090;
        server_name sitemaps.example.com;

        location / {
            root html;
            index index.html;
            if (!-f $request_filename) {
                rewrite ^/(.*)-sitemap.xml$ /sitemap/$1 last;
            }
        }

        location /sitemap {
            perl Sitemap::handler;
        }
    }
}
```

## Perl Module (`lib/Sitemap.pm`)

```perl
package Sitemap;
use nginx;
use LWP::Simple;

our $basedir = "/usr/local/nginx/html";

sub handler {
    my $r = shift;
    my $uri = $r->uri;
    $uri =~ s!^/*sitemap/*!!g;
    $uri =~ s!/.*!!g;

    my $sitemap_url = "http://$uri/sitemap.xml";
    my $sitemap_data = get($sitemap_url);

    return 404 if $sitemap_data !~ m/urlset/;

    my $sitemap_file = "$basedir/$uri-sitemap.xml";
    open "F", ">$sitemap_file";
    print F $sitemap_data;
    close("F");

    $r->send_http_header("application/xml");
    $r->sendfile($sitemap_file);
    $r->flush;
    return OK;
}

1;
```

## Domain robots.txt

```
User-agent: *
Disallow: /tmp/
sitemap: http://sitemaps.example.com/mydomain.com-sitemap.xml
```


