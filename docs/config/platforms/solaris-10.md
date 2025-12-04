---
title: Solaris 10 (Legacy)
description: Building and installing NGINX on Solaris 10 Update 5.
---

# Installing NGINX on Solaris 10

!!! warning "Legacy Documentation"
    This page documents installing NGINX on Solaris 10, which reached end of support in January 2021. The instructions reference outdated software versions. Consider migrating to a supported operating system.

## Prerequisites

Required packages:
- SUNWbtool, SUNWtoo, SUNWlibmr, SUNWlibm
- Sun Studio 12 Compiler

### Set PATH

```bash
export PATH=$PATH:/opt/SUNWSpro/bin:/usr/ccs/bin:/usr/sfw/bin
```

## Build PCRE

```bash
cd /usr/src
wget https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.42/pcre2-10.42.tar.gz
gtar -zxf pcre2-10.42.tar.gz
cd pcre2-10.42

./configure --disable-cpp CFLAGS="-g -O3" \
    CC="/opt/SUNWspro/bin/cc -m64" \
    --prefix=/opt/local \
    --enable-unicode

make && make install
```

## Build OpenSSL

```bash
cd /usr/src
# Download OpenSSL 3.x from openssl.org
wget https://github.com/openssl/openssl/releases/download/openssl-3.0.11/openssl-3.0.11.tar.gz
gtar -zxf openssl-3.0.11.tar.gz
cd openssl-3.0.11

./Configure solaris64-x86_64-cc threads shared \
    --prefix=/opt/local --openssldir=/opt/local/openssl

make && make install
```

## Build NGINX

```bash
cd /usr/src
wget https://nginx.org/download/nginx-1.26.0.tar.gz
gtar -zxf nginx-1.26.0.tar.gz
cd nginx-1.26.0

CC="cc" ./configure \
    --prefix=/opt/local/nginx \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-cc-opt="-I /opt/local/include" \
    --with-ld-opt="-L /opt/local/lib -R /lib -R /usr/lib -R /opt/local/lib"

make && make install
```

## SMF Service

### Method Script (`/lib/svc/method/svc-nginx`)

```bash
#!/bin/sh
NGINX_CMD="/opt/local/nginx/sbin/nginx"
NGINX_CONF="/opt/local/nginx/conf/nginx.conf"

start() {
    echo "Starting NGINX: \c"
    $NGINX_CMD -c $NGINX_CONF &
    [ $? -eq 0 ] && echo "ok" || echo "failed"
}

stop() {
    echo "Stopping NGINX: \c"
    kill $(pgrep -f $NGINX_CMD)
    [ $? -eq 0 ] && echo "ok" || echo "failed"
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; start ;;
    *) echo "Usage: $0 {start|stop|restart}" ;;
esac
```

### Manifest (`/var/svc/manifest/network/nginx.xml`)

```xml
<?xml version="1.0"?>
<!DOCTYPE service_bundle SYSTEM "/usr/share/lib/xml/dtd/service_bundle.dtd.1">
<service_bundle type='manifest' name='nginx'>
<service name='network/nginx' type='service' version='1'>
    <create_default_instance enabled='false' />
    <single_instance />
    <exec_method type='method' name='start' 
        exec='/lib/svc/method/svc-nginx start' timeout_seconds='60'/>
    <exec_method type='method' name='stop' 
        exec='/lib/svc/method/svc-nginx stop' timeout_seconds='60' />
</service>
</service_bundle>
```

### Enable Service

```bash
chmod 555 /lib/svc/method/svc-nginx
chmod 444 /var/svc/manifest/network/nginx.xml
svccfg -v import /var/svc/manifest/network/nginx.xml
svcadm enable nginx
```
