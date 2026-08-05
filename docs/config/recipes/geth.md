---
title: NGINX Geth Ethereum Configuration Guide
description: Configure NGINX as reverse proxy for Geth go-ethereum node with RPC and WebSocket endpoints for Web3.js integration.
keywords: nginx, geth, ethereum, go-ethereum, rpc, websocket, web3, blockchain, cryptocurrency, node
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - nginx
  - geth
  - ethereum
  - blockchain
  - websocket
  - rpc
  - web3
---

# Geth (go-ethereum)

Geth is the Go implementation of Ethereum.

This configuration exposes Geth's RPC and WebSocket interfaces via NGINX.

## Start Geth

```bash
./geth --cache 4096 \
    --rpc --rpcaddr "127.0.0.1" --rpccorsdomain "*" --rpcport "8545" \
    --rpcapi "db,eth,net,web3,personal" \
    --ws --wsport 8546 --wsaddr "127.0.0.1" --wsorigins "*" \
    --wsapi "web3,eth" --maxpeers=100
```

## NGINX Configuration

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name localhost;

    # WebSocket endpoint
    location ^~ /ws {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header X-NginX-Proxy true;
        proxy_pass http://127.0.0.1:8546/;
    }

    # RPC endpoint
    location ^~ /rpc {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_set_header X-NginX-Proxy true;
        proxy_pass http://127.0.0.1:8545/;
    }
}
```

## Testing with Web3.js

```javascript
var Web3 = require('web3');
var web3 = new Web3();

// HTTP RPC
web3.setProvider(new Web3.providers.HttpProvider('http://SERVER_IP/rpc'));

// WebSocket
web3.setProvider(new Web3.providers.WebsocketProvider('ws://SERVER_IP/ws'));
```


