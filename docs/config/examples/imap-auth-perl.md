---
title: IMAP Auth with Perl
description: Using embedded Perl for IMAP/POP3 authentication.
---

# IMAP Authentication with Embedded Perl

!!! warning
    This blocks the NGINX worker during DB queries. Consider using external auth scripts for high-traffic deployments.

## Build NGINX

```bash
./configure --with-http_perl_module --with-mail
```

## NGINX Configuration

```nginx
user nobody;
worker_processes 1;
error_log logs/error.log info;

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    perl_modules perl/lib;
    perl_require mailauth.pm;

    server {
        location /auth {
            perl mailauth::handler;
        }
    }
}

mail {
    auth_http 127.0.0.1:80/auth;

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

## Perl Module (`perl/lib/mailauth.pm`)

```perl
package mailauth;
use nginx;
use DBI;

my $dsn = "DBI:mysql:database=DBNAME;host=HOSTNAME";
our $dbh = DBI->connect_cached($dsn, 'user', 'pass', {AutoCommit => 1});
our $sth = $dbh->prepare(
    "SELECT password, mail_server FROM mailaccounts WHERE username=? LIMIT 1"
);

our $mail_server_ip = {
    'mailhost01' => "192.168.1.22",
    'mailhost02' => "192.168.1.33",
};

our $protocol_ports = {
    'pop3' => 110,
    'imap' => 143,
};

sub handler {
    my $r = shift;
    my $auth_ok = 0;

    $sth->execute($r->header_in("Auth-User"));
    my $hash = $sth->fetchrow_hashref();

    if (crypt($r->header_in("Auth-Pass"), $hash->{'password'}) 
        eq $r->header_in("Auth-Pass")) {
        $auth_ok = 1;
    }

    if ($auth_ok == 1) {
        $r->header_out("Auth-Status", "OK");
        $r->header_out("Auth-Server", $mail_server_ip->{$hash->{'mail_server'}});
        $r->header_out("Auth-Port", $protocol_ports->{$r->header_in("Auth-Protocol")});
    } else {
        $r->header_out("Auth-Status", "Invalid login or password");
    }

    $r->send_http_header("text/html");
    return OK;
}

1;
```


