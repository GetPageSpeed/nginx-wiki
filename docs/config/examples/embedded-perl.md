---
title: Embedded Perl
description: Examples of using embedded Perl in NGINX configurations.
---

# Embedded Perl

NGINX can embed Perl for dynamic content generation.

## JavaScript Minification

This example minifies JavaScript files on-the-fly using the JavaScript::Minifier CPAN module.

### NGINX Configuration

```nginx
http {
    perl_modules perl;
    perl_require Javascript/Minifier.pm;
    perl_require Minify.pm;

    root /var/www;

    server {
        location / {
            index index.html index.htm;
        }

        location ~ \.js$ {
            perl Minify::handler;
        }
    }
}
```

### Perl Module (perl/Minify.pm)

```perl
package Minify;
use nginx;
use JavaScript::Minifier qw(minify);

sub handler {
    my $r = shift;
    my $cache_dir = "/tmp";
    my $cache_file = $r->uri;
    $cache_file =~ s!/!_!g;
    $cache_file = join("/", $cache_dir, $cache_file);
    my $filename = $r->filename;

    return DECLINED unless -f $filename;

    if (! -f $cache_file) {
        open(INFILE, $filename) or die "Error reading file: $!";
        open(OUTFILE, '>' . $cache_file) or die "Error writing file: $!";
        minify(input => *INFILE, outfile => *OUTFILE);
        close(INFILE);
        close(OUTFILE);
    }

    $r->send_http_header("application/javascript");
    $r->sendfile($cache_file);
    return OK;
}

1;
__END__
```

### Requirements

Install the JavaScript::Minifier module from CPAN:

```bash
cpan JavaScript::Minifier
```

For CSS minification, use CSS::Minifier:

```bash
cpan CSS::Minifier
```
