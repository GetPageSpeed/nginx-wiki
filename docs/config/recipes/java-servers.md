---
title: NGINX Java Application Server Configuration
description: Configure NGINX as a reverse proxy for Jetty, Tomcat, and GlassFish Java servers with load balancing and static file serving.
keywords: nginx, java, jetty, tomcat, glassfish, reverse proxy, jsp, servlet, load balancing, jvm
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - java
  - jetty
  - tomcat
  - glassfish
  - reverse proxy
  - load balancing
---

# Java Servers

NGINX works as a reverse proxy in front of Java application servers like Jetty, GlassFish, and Tomcat.

!!! note "Deployment"
    You cannot deploy using `.war` files directly. The application must be deployed into a folder so NGINX can serve static files (images, CSS, JavaScript) directly without involving the Java server.

---

## Basic Configuration

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN;
    root /PATH/TO/YOUR/WEB/APPLICATION;

    location / {
        index index.jsp;
    }

    # Proxy .do requests to Java server
    location ~ \.do$ {
        proxy_pass http://localhost:8080;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }

    # Proxy .jsp requests to Java server
    location ~ \.jsp$ {
        proxy_pass http://localhost:8080;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }

    # Proxy servlet paths to Java server
    location ^~ /servlets/ {
        proxy_pass http://localhost:8080;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }
}
```

---

## Jetty Context Configuration

Configure your web application context in `jetty/contexts/YOUR_APP.xml`:

```xml
<?xml version="1.0"?>
<!DOCTYPE Configure PUBLIC "-//Mort Bay Consulting//DTD Configure//EN" 
    "http://jetty.mortbay.org/configure.dtd">
<Configure class="org.mortbay.jetty.webapp.WebAppContext">
    <Set name="contextPath">/</Set>
    <Set name="resourceBase">
        <SystemProperty name="jetty.home" default="."/>/webapps/YOUR_APP
    </Set>
    <Set name="virtualHosts">
        <Array type="java.lang.String">
            <Item>YOUR_DOMAIN</Item>
        </Array>
    </Set>
</Configure>
```

---

## Securing the Java Server

If NGINX and Java run on the same server, block external access to port 8080:

### Using iptables

```bash
/sbin/iptables -A INPUT -p tcp -i eth0 --dport 8080 -j REJECT --reject-with tcp-reset
```

### Binding Jetty to localhost

In `conf/jetty.xml`:

```xml
<Set name="host">
    <SystemProperty name="jetty.host" default="localhost"/>
</Set>
```

Or in embedded Jetty code:

```java
Server server = new Server();
SelectChannelConnector connector = new SelectChannelConnector();
connector.setHost("localhost");  // bind to localhost only
connector.setPort(8080);
server.addConnector(connector);
server.start();
server.join();
```

---

## Upstream with Load Balancing

For multiple Java servers:

```nginx
upstream java_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name YOUR_DOMAIN;
    root /PATH/TO/YOUR/WEB/APPLICATION;

    location / {
        index index.jsp;
    }

    location ~ \.(do|jsp)$ {
        proxy_pass http://java_backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }
}
```


