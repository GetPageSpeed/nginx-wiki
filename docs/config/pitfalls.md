---
title: NGINX Pitfalls and Common Mistakes - Configuration Errors to Avoid
description: Avoid common NGINX configuration mistakes. Learn about chmod 777 dangers, root inside location, proxy_pass with trailing slashes, if directive issues, and more pitfalls that break NGINX setups.
keywords: nginx pitfalls, nginx common mistakes, nginx configuration errors, nginx troubleshooting, nginx if is evil, nginx root location, nginx proxy_pass, nginx best practices, nginx debugging
author: NGINX Community
date: 2024-01-01
updated: 2025-01-21
schema_type: TechArticle
tags:
  - configuration
  - troubleshooting
  - best-practices
  - pitfalls
---

# Pitfalls and Common Mistakes

New and old users alike can run into a pitfall. Below we outline issues that we see frequently as well as explain how to resolve those issues. In the #nginx IRC channel on Libera Chat, we see these issues frequently.

## This Guide Says

The most frequent issue we see happens when someone attempts to just copy and paste a configuration snippet from some other guide. Not all guides out there are wrong, but a scary number of them are.

These docs were created and reviewed by community members that work directly with all types of NGINX users. This specific document exists only because of the volume of common and recurring issues that community members see.

## My Issue Isn't Listed

You don't see something in here related to your specific issue. Maybe we didn't point you here because of the exact issue you're experiencing. Don't skim this page and assume you were sent here for no reason. You were sent here because something you did wrong is listed here.

When it comes to supporting many users on many issues, community members don't want to support broken configurations. Fix your configuration before asking for help. Fix your configuration by reading through this. Don't just skim it.

---

## Chmod 777

**NEVER use `777`.** It might be one nifty number, but even in testing it's a sign of having no clue what you're doing. Look at the permissions in the whole path and think through what's going on.

To easily display all the permissions on a path, you can use:

```bash
namei -om /path/to/check
```

---

## Root inside Location Block

**BAD:**

```nginx
server {
    server_name www.example.com;
    location / {
        root /var/www/nginx-default/;
        # [...]
      }
    location /foo {
        root /var/www/nginx-default/;
        # [...]
    }
    location /bar {
        root /some/other/place;
        # [...]
    }
}
```

This works. Putting root inside of a `location` block will work and it's perfectly valid. What's wrong is when you start adding `location` blocks. If you add a root to every location block then a `location` block that isn't matched will have no root. Therefore, it is important that a root directive occur prior to your `location` blocks, which can then override this directive if they need to.

**GOOD:**

```nginx
server {
    server_name www.example.com;
    root /var/www/nginx-default/;
    location / {
        # [...]
    }
    location /foo {
        # [...]
    }
    location /bar {
        root /some/other/place;
        # [...]
    }
}
```

---

## Multiple Index Directives

**BAD:**

```nginx
http {
    index index.php index.htm index.html;
    server {
        server_name www.example.com;
        location / {
            index index.php index.htm index.html;
            # [...]
        }
    }
    server {
        server_name example.com;
        location / {
            index index.php index.htm index.html;
            # [...]
        }
        location /foo {
            index index.php;
            # [...]
        }
    }
}
```

Why repeat so many lines when not needed? Simply use the `index` directive one time. It only needs to occur in your `http{}` block and it will be inherited below.

**GOOD:**

```nginx
http {
    index index.php index.htm index.html;
    server {
        server_name www.example.com;
        location / {
            # [...]
        }
    }
    server {
        server_name example.com;
        location / {
            # [...]
        }
        location /foo {
            # [...]
        }
    }
}
```

---

## Using `if`

There is a little page about using `if` statements. It's called [If Is Evil](if-is-evil.md) and you really should check it out.

---

## Server Name (If)

**BAD:**

```nginx
server {
    server_name example.com *.example.com;
        if ($host ~* ^www\.(.+)) {
            set $raw_domain $1;
            rewrite ^/(.*)$ $raw_domain/$1 permanent;
        }
        # [...]
    }
}
```

There are actually three problems here. The first being the `if`. When NGINX receives a request—no matter what is the subdomain being requested, be it www.example.com or just the plain example.com—this `if` directive is **always** evaluated. Since you're requesting NGINX to check for the Host header for **every request**, it's extremely inefficient. You should avoid it. Instead use two `server` directives.

**GOOD:**

```nginx
server {
    server_name www.example.com;
    return 301 $scheme://example.com$request_uri;
}
server {
    server_name example.com;
    # [...]
}
```

Besides making the configuration file easier to read, this approach decreases NGINX processing requirements. We got rid of the spurious `if`. We're also using `$scheme` which doesn't hardcode the URI scheme you're using, be it http or https.

---

## Check (If) File Exists

Using `if` to ensure a file exists is horrible. If you have any recent version of NGINX you should look at `try_files` which just made life much easier.

**BAD:**

```nginx
server {
    root /var/www/example.com;
    location / {
        if (!-f $request_filename) {
            break;
        }
    }
}
```

**GOOD:**

```nginx
server {
    root /var/www/example.com;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

What we changed is that we try to see if `$uri` exists without requiring `if`. Using `try_files` means that you can test a sequence. If `$uri` doesn't exist, try `$uri/`, if that doesn't exist try a fallback location.

---

## Front Controller Pattern Web Apps

"Front Controller Pattern" designs are popular and are used on many of the most popular PHP software packages. For Drupal, Joomla, etc., just use this:

```nginx
try_files $uri $uri/ /index.php?q=$uri&$args;
```

Note - the parameter names are different based on the package you're using:

- `q` is the parameter used by Drupal, Joomla, WordPress
- `page` is used by CMS Made Simple

Some software don't even need the query string and can read from REQUEST_URI. For example, WordPress supports this:

```nginx
try_files $uri $uri/ /index.php;
```

---

## Passing Uncontrolled Requests to PHP

Many example NGINX configurations for PHP on the web advocate passing every URI ending in `.php` to the PHP interpreter. Note that this presents a serious security issue on most PHP setups as it may allow arbitrary code execution by third parties.

The problem section usually looks like this:

```nginx
location ~* \.php$ {
    fastcgi_pass backend;
    # [...]
}
```

Here, every request ending in `.php` will be passed to the FastCGI backend. The issue with this is that the default PHP configuration tries to guess which file you want to execute if the full path does not lead to an actual file on the filesystem.

For instance, if a request is made for `/forum/avatar/1232.jpg/file.php` which does not exist but if `/forum/avatar/1232.jpg` does, the PHP interpreter will process `/forum/avatar/1232.jpg` instead. If this contains embedded PHP code, this code will be executed accordingly.

**Options for avoiding this:**

1. Set `cgi.fix_pathinfo=0` in `php.ini`
2. Ensure that NGINX only passes specific PHP files for execution:

```nginx
location ~* (file_a|file_b|file_c)\.php$ {
    fastcgi_pass backend;
    # [...]
}
```

3. Specifically disable the execution of PHP files in any directory containing user uploads:

```nginx
location /uploaddir {
    location ~ \.php$ {return 403;}
    # [...]
}
```

4. Use the `try_files` directive to filter out the problem condition:

```nginx
location ~* \.php$ {
    try_files $uri =404;
    fastcgi_pass backend;
    # [...]
}
```

---

## Taxing Rewrites

Don't feel bad here, it's easy to get confused with regular expressions. In fact, it's so easy to do that we should make an effort to keep them neat and clean.

**BAD:**

```nginx
rewrite ^/(.*)$ http://example.com/$1 permanent;
```

**GOOD:**

```nginx
rewrite ^ http://example.com$request_uri? permanent;
```

**BETTER:**

```nginx
return 301 http://example.com$request_uri;
```

The first rewrite captures the full URI minus the first slash. By using the built-in variable `$request_uri` we can effectively avoid doing any capturing or matching at all.

---

## Proxy Everything

**BAD:**

```nginx
server {
    server_name _;
    root /var/www/site;
    location / {
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_pass unix:/tmp/phpcgi.socket;
    }
}
```

In this instance, you pass EVERYTHING to PHP. Why? The `try_files` directive exists for an amazing reason: It tries files in a specific order. NGINX can first try to serve the static content, and if it can't, it moves on. This means PHP doesn't get involved at all. MUCH faster.

**GOOD:**

```nginx
server {
    server_name _;
    root /var/www/site;
    location / {
        try_files $uri $uri/ @proxy;
    }
    location @proxy {
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_pass unix:/tmp/phpcgi.socket;
    }
}
```

---

## Config Changes Not Reflected

Browser cache. Your configuration may be perfect but you'll sit there and beat your head against a cement wall for a month. What's wrong is your browser cache.

**The fix:**

- In Firefox press Ctrl+Shift+Delete, check Cache, click Clear Now.
- Use curl for testing.

---

## VirtualBox

If this does not work, and you're running NGINX on a virtual machine in VirtualBox, it may be `sendfile()` that is causing the trouble. Simply comment out the sendfile directive or set it to "off":

```nginx
sendfile off;
```

---

## Missing (disappearing) HTTP Headers

If you do not explicitly set `underscores_in_headers on;`, NGINX will silently drop HTTP headers with underscores (which are perfectly valid according to the HTTP standard). This is done in order to prevent ambiguities when mapping headers to CGI variables as both dashes and underscores are mapped to underscores during that process.

---

## Not Using Standard Document Root Locations

Some directories in any file system should never be used for hosting data from. These include `/` and `root`. You should never use these as your document root.

**NEVER DO THIS:**

```nginx
server {
    root /;

    location / {
        try_files /web/$uri $uri @php;
    }

    location @php {
        # [...]
    }
}
```

When a request is made for `/foo`, the request is passed to php because the file isn't found. This can appear fine, until a request is made for `/etc/passwd`. Yup, you just gave us a list of all users on that server.

The [File System Hierarchy](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard) defines where data should exist. You want your web content to exist in either `/var/www/`, `/srv`, or `/usr/share/www`.

---

## Using SSLv3 with HTTPS

Due to the POODLE vulnerability in SSLv3, it is advised to not use SSLv3 in your SSL-enabled sites:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
```

---

## Automated Configuration Checking

Many of the pitfalls listed above can be detected automatically using [Gixy](https://gixy.org/), a static analyzer for NGINX configuration files.

```bash
# Install gixy
pip install gixy

# Check your configuration
gixy /etc/nginx/nginx.conf
```

Gixy will catch issues like:

- Dangerous `if` directive usage
- `add_header` directive problems
- Host header forgery vulnerabilities
- SSRF via misconfigured `proxy_pass`
- HTTP splitting issues

!!! tip "Validate Before Deploying"
    Always run `gixy` on your configuration before reloading NGINX in production.


