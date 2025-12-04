---
title: CGI with fcgiwrap
description: Running CGI applications over FastCGI with fcgiwrap.
---

# CGI with fcgiwrap

Use fcgiwrap to run CGI applications with NGINX.

## Install on Debian/Ubuntu

```bash
apt install fcgiwrap
```

Then include the example configuration in your server block:

```bash
cp /usr/share/doc/fcgiwrap/examples/nginx.conf /etc/nginx/fcgiwrap.conf
```

```nginx
server {
    # ... other config ...
    
    # FastCGI support for CGI scripts
    include /etc/nginx/fcgiwrap.conf;
}
```

## Manual Installation

### Build fcgiwrap

```bash
apt install git-core build-essential libfcgi-dev autoconf libtool automake
cd /usr/local/src/
git clone git://github.com/gnosek/fcgiwrap.git
cd fcgiwrap
autoreconf -i
./configure
make
mv fcgiwrap /usr/local/bin/
```

### Init Script

Save as `/etc/init.d/fcgiwrap`:

```perl
#!/usr/bin/perl
use strict;
use warnings FATAL => qw(all);
use IO::Socket::UNIX;

my $bin_path = '/usr/local/bin/fcgiwrap';
my $socket_path = $ARGV[0] || '/tmp/cgi.sock';
my $num_children = $ARGV[1] || 1;

close STDIN;
unlink $socket_path;

my $socket = IO::Socket::UNIX->new(
    Local => $socket_path,
    Listen => 100,
);

die "Cannot create socket at $socket_path: $!\n" unless $socket;

for (1 .. $num_children) {
    my $pid = fork;
    die "Cannot fork: $!" unless defined $pid;
    next if $pid;
    exec $bin_path;
    die "Failed to exec $bin_path: $!\n";
}
```

Make executable:

```bash
chmod +x /etc/init.d/fcgiwrap
```

Add to `/etc/rc.local`:

```bash
sudo -u www-data /etc/init.d/fcgiwrap
```

## NGINX Configuration

```nginx
location /cgi-bin/ {
    fastcgi_pass unix:/tmp/cgi.sock;
    fastcgi_param SCRIPT_FILENAME /var/www/cgi-bin$fastcgi_script_name;
    include fastcgi_params;
}
```


