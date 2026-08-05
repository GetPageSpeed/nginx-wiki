---
title: NGINX on Solaris and illumos - Installation Guide
description: Build and install NGINX on Solaris 11.4+ and illumos (OmniOS, SmartOS) with SMF service configuration and compile instructions.
keywords: nginx solaris, nginx illumos, nginx omnios, nginx smartos, nginx smf, nginx solaris installation
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - installation
  - solaris
  - illumos
  - smf
  - unix
  - compilation
---

# Installing NGINX on Solaris / illumos

!!! warning "Legacy Platform"
    Solaris and illumos are niche platforms for NGINX. For production deployments, Linux (RHEL, Debian, Ubuntu) is recommended where pre-built packages with third-party modules are readily available.

## Solaris 11.4+

Modern Solaris 11.4+ includes recent versions of PCRE and OpenSSL.

### Install Build Dependencies

```bash
pkg install developer/gcc
pkg install system/header
pkg install developer/build/make
pkg install library/pcre2
pkg install library/security/openssl-3
```

### Compile NGINX

```bash
# Download latest stable
wget https://nginx.org/download/nginx-1.26.2.tar.gz
tar xzf nginx-1.26.2.tar.gz
cd nginx-1.26.2

# Configure with common modules
./configure \
    --prefix=/opt/nginx \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_gzip_static_module \
    --with-pcre \
    --with-stream \
    --with-stream_ssl_module

make -j$(nproc)
sudo make install
```

---

## illumos (OmniOS, SmartOS)

illumos distributions like OmniOS provide NGINX packages.

### OmniOS

```bash
# From OmniOS extra repo
pkg install ooce/server/nginx
```

### SmartOS

```bash
pkgin install nginx
```

---

## SMF Service (Solaris/illumos)

### Create Method Script

Save as `/lib/svc/method/svc-nginx`:

```bash
#!/bin/sh
NGINX_CMD="/opt/nginx/sbin/nginx"
NGINX_CONF="/opt/nginx/conf/nginx.conf"

start() {
    echo "Starting NGINX: \c"
    $NGINX_CMD -c $NGINX_CONF
    [ $? -eq 0 ] && echo "ok" || echo "failed"
}

stop() {
    echo "Stopping NGINX: \c"
    $NGINX_CMD -s quit
    [ $? -eq 0 ] && echo "ok" || echo "failed"
}

reload() {
    echo "Reloading NGINX: \c"
    $NGINX_CMD -s reload
    [ $? -eq 0 ] && echo "ok" || echo "failed"
}

case "$1" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; sleep 1; start ;;
    reload)  reload ;;
    *) echo "Usage: $0 {start|stop|restart|reload}"; exit 1 ;;
esac
```

### Create SMF Manifest

Save as `/var/svc/manifest/network/nginx.xml`:

```xml
<?xml version="1.0"?>
<!DOCTYPE service_bundle SYSTEM "/usr/share/lib/xml/dtd/service_bundle.dtd.1">
<service_bundle type='manifest' name='nginx'>
  <service name='network/nginx' type='service' version='1'>
    <create_default_instance enabled='false' />
    <single_instance />
    
    <dependency name='network' grouping='require_all' restart_on='error' type='service'>
      <service_fmri value='svc:/milestone/network:default'/>
    </dependency>
    
    <dependency name='filesystem' grouping='require_all' restart_on='error' type='service'>
      <service_fmri value='svc:/system/filesystem/local'/>
    </dependency>
    
    <exec_method type='method' name='start'
        exec='/lib/svc/method/svc-nginx start' timeout_seconds='60'/>
    <exec_method type='method' name='stop'
        exec='/lib/svc/method/svc-nginx stop' timeout_seconds='60' />
    <exec_method type='method' name='refresh'
        exec='/lib/svc/method/svc-nginx reload' timeout_seconds='60' />
        
    <property_group name='startd' type='framework'>
      <propval name='duration' type='astring' value='contract'/>
    </property_group>
    
    <stability value='Stable' />
    <template>
      <common_name>
        <loctext xml:lang='C'>NGINX Web Server</loctext>
      </common_name>
    </template>
  </service>
</service_bundle>
```

### Enable the Service

```bash
chmod 555 /lib/svc/method/svc-nginx
chown root:bin /lib/svc/method/svc-nginx

chmod 444 /var/svc/manifest/network/nginx.xml
chown root:sys /var/svc/manifest/network/nginx.xml

svccfg -v import /var/svc/manifest/network/nginx.xml
svcadm enable nginx
```

### Manage the Service

```bash
# Check status
svcs -l nginx

# Start/stop/restart
svcadm enable nginx
svcadm disable nginx
svcadm restart nginx

# Reload configuration
svcadm refresh nginx
```

---

## See Also

- [Building NGINX from Source](../../modules-dev/compiling.md)
