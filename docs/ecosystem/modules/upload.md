---
title: NGINX Upload Module - File Upload Handling Guide
description: Configure NGINX upload module for multipart/form-data file uploads with resumable uploads, checksums, and rate limiting.
keywords: nginx upload, nginx file upload, multipart form data, nginx upload module, resumable upload, nginx file handling
author: NGINX Community
date: 2025-12-05
updated: 2026-08-05
schema_type: TechArticle
tags:
  - modules
  - file-upload
  - multipart
  - form-data
  - file-handling
---

# Upload Module

**nginx-upload-module** parses request bodies, stores uploaded files to a directory, then passes an altered request to a backend.

:octicons-repo-16: **Repository**: [vkholodkov/nginx-upload-module](https://github.com/vkholodkov/nginx-upload-module/tree/2.2)  
:octicons-package-16: **NGINX Extras**: [nginx-module-upload](https://nginx-extras.getpagespeed.com/modules/upload/)

---

## Installation

=== "RHEL/CentOS/AlmaLinux/Rocky (Recommended)"
    ```bash
    sudo dnf -y install https://extras.getpagespeed.com/release-latest.rpm
    sudo dnf -y install nginx-module-upload
    ```
    
    Enable in `/etc/nginx/nginx.conf`:
    ```nginx
    load_module modules/ngx_http_upload_module.so;
    ```

=== "From Source"
    ```bash
    git clone https://github.com/vkholodkov/nginx-upload-module.git
    cd nginx-1.x.x
    ./configure --add-module=../nginx-upload-module
    make && sudo make install
    ```

---

## Directives

### upload_pass

| | |
|---|---|
| **Syntax** | `upload_pass <location>` |
| **Default** | — |
| **Context** | server, location |

Specifies location to pass the request body to. File fields are replaced by form fields containing file metadata.

### upload_store

| | |
|---|---|
| **Syntax** | `upload_store <directory> [<level 1> [<level 2>]...]` |
| **Default** | — |
| **Context** | server, location |

Directory for storing uploaded files. Can be hashed; subdirectories must exist beforehand.

### upload_resumable

| | |
|---|---|
| **Syntax** | `upload_resumable on|off` |
| **Default** | `off` |
| **Context** | http, server, location |

Enables resumable uploads.

### upload_store_access

| | |
|---|---|
| **Syntax** | `upload_store_access <mode>` |
| **Default** | `user:rw` |
| **Context** | server, location |

Access mode for created output files.

### upload_set_form_field

| | |
|---|---|
| **Syntax** | `upload_set_form_field <name> <value>` |
| **Default** | — |
| **Context** | server, location |

Specifies form fields to generate for each uploaded file. Available variables:

- `$upload_field_name` — original file field name
- `$upload_content_type` — content type of uploaded file
- `$upload_file_name` — original filename (path stripped)
- `$upload_tmp_path` — path to stored file

### upload_aggregate_form_field

| | |
|---|---|
| **Syntax** | `upload_aggregate_form_field <name> <value>` |
| **Default** | — |
| **Context** | server, location |

Generates form fields with aggregate attributes after file upload completes:

- `$upload_file_md5` / `$upload_file_md5_uc` — MD5 checksum
- `$upload_file_sha1` / `$upload_file_sha1_uc` — SHA1 checksum
- `$upload_file_crc32` — CRC32 (hex)
- `$upload_file_size` — size in bytes
- `$upload_file_number` — ordinal number in request

!!! warning
    MD5/SHA1 variables consume additional resources.

### upload_pass_form_field

| | |
|---|---|
| **Syntax** | `upload_pass_form_field <regex>` |
| **Default** | — |
| **Context** | server, location |

Regex pattern for field names to pass through to backend.

### upload_cleanup

| | |
|---|---|
| **Syntax** | `upload_cleanup <status> [<status>...]` |
| **Default** | — |
| **Context** | server, location |

HTTP statuses (400-599) that trigger removal of uploaded files. Supports ranges:

```nginx
upload_cleanup 400 404 499 500-505;
```

### upload_max_file_size

| | |
|---|---|
| **Syntax** | `upload_max_file_size <size>` |
| **Default** | `0` (unlimited) |
| **Context** | server, location |

Soft limit on file size. For hard limits, use `client_max_body_size`.

### upload_limit_rate

| | |
|---|---|
| **Syntax** | `upload_limit_rate <rate>` |
| **Default** | `0` (unlimited) |
| **Context** | main, server, location |

Upload rate limit in bytes per second.

---

## Example Configuration

```nginx
server {
    client_max_body_size 100m;
    listen 80;

    location /upload {
        upload_pass @backend;

        # Store files (create subdirs 0-9 first)
        upload_store /tmp 1;
        upload_store_access user:r;

        # Set form fields
        upload_set_form_field $upload_field_name.name "$upload_file_name";
        upload_set_form_field $upload_field_name.content_type "$upload_content_type";
        upload_set_form_field $upload_field_name.path "$upload_tmp_path";

        # Aggregate fields
        upload_aggregate_form_field "$upload_field_name.md5" "$upload_file_md5";
        upload_aggregate_form_field "$upload_field_name.size" "$upload_file_size";

        # Pass through these fields
        upload_pass_form_field "^submit$|^description$";

        # Cleanup on error
        upload_cleanup 400 404 499 500-505;
    }

    location @backend {
        proxy_pass http://localhost:8080;
    }
}
```

## Example HTML Form

```html
<form method="POST" enctype="multipart/form-data" action="/upload">
    <input type="file" name="file1"><br>
    <input type="file" name="file2"><br>
    <input type="submit" name="submit" value="Upload">
</form>
```


