---
title: IMAP Auth with PHP
description: Using a PHP script as the IMAP/POP3 authentication backend.
---

# IMAP Authentication with PHP

Use a PHP script to authenticate users and route to backend mail servers.

## Setup

- Proxy server: 192.168.1.1
- Backend servers: 192.168.1.22, 192.168.1.33
- Auth web server: 192.168.1.44

## NGINX Configuration

```nginx
user nobody;
worker_processes 1;
error_log logs/error.log info;
pid logs/nginx.pid;

events {
    worker_connections 1024;
    multi_accept on;
}

mail {
    auth_http 192.168.1.44:80/mail/auth.php;
    pop3_capabilities "TOP" "USER";
    imap_capabilities "IMAP4rev1" "UIDPLUS";

    server {
        listen 110;
        protocol pop3;
        proxy on;
    }

    server {
        listen 143;
        protocol imap;
        proxy on;
    }
}
```

## PHP Auth Script (`/mail/auth.php`)

```php
<?php
if (!isset($_SERVER["HTTP_AUTH_USER"]) || !isset($_SERVER["HTTP_AUTH_PASS"])) {
    fail();
}

$username = $_SERVER["HTTP_AUTH_USER"];
$userpass = $_SERVER["HTTP_AUTH_PASS"];
$protocol = $_SERVER["HTTP_AUTH_PROTOCOL"];

// Default backend port
$backend_port = 110;
if ($protocol == "imap") {
    $backend_port = 143;
}
if ($protocol == "smtp") {
    $backend_port = 25;
}

// Backend IP mapping
$backend_ip["mailhost01"] = "192.168.1.22";
$backend_ip["mailhost02"] = "192.168.1.33";

// Authenticate
if (!authuser($username, $userpass)) {
    fail();
    exit;
}

// Get backend server
$userserver = getmailserver($username);
$server_ip = isset($backend_ip[$userserver]) ? $backend_ip[$userserver] : $userserver;

pass($server_ip, $backend_port);

function authuser($user, $pass) {
    // Decode NGINX-encoded characters
    $pass = str_replace('%20', ' ', $pass);
    $pass = str_replace('%25', '%', $pass);
    
    // Add your authentication logic here (LDAP, database, etc.)
    return true;
}

function getmailserver($user) {
    // Route users to backends
    if (in_array(substr($user, 0, 1), array("a", "c", "f", "g"))) {
        return "mailhost01";
    } else {
        return "mailhost02";
    }
}

function fail() {
    header("Auth-Status: Invalid login or password");
    exit;
}

function pass($server, $port) {
    header("Auth-Status: OK");
    header("Auth-Server: $server");
    header("Auth-Port: $port");
    exit;
}
```


