compose_base = """version: "3"

services:

  proxy:
    build:
      context: .
      dockerfile: nginx.dockerfile
    ports:
      - 80:80
    depends_on:
      - """

def depends_on(i):
    return "\n      - ".join(f"nb{x}" for x in range(i))

def nb(i):
    return f"""
  nb{i}:
    build:
      context: .
      dockerfile: notebook.dockerfile
"""

nginx_base = """
worker_processes  5;  ## Default: 1
error_log  error.log;
pid        nginx.pid;
worker_rlimit_nofile 8192;

events {
  worker_connections  4096;  ## Default: 1024
}

http {

  default_type application/octet-stream;
  log_format   main '$remote_addr - $remote_user [$time_local]  $status '
    '"$request" $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log   access.log  main;
  sendfile     on;
  tcp_nopush   on;
  server_names_hash_bucket_size 128; # this seems to be required for some vhosts


  server {
    listen 80;
    server_name localhost;
    location / {
      proxy_pass      http://notebooks;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $http_host;
    proxy_http_version 1.1;
    proxy_redirect off;
    proxy_buffering off;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
    }
  }
"""

def nginx_notebooks(x):
    servers = "\n\t".join(f"server nb{i}:8888;" for i in range(x))

    return f"""
  upstream notebooks {{
      ip_hash;
      {servers}
  }}
"""

n_notebooks = 10

compose_full = compose_base + depends_on(n_notebooks) + ''.join(nb(i) for i in range(n_notebooks))
nginx_full = nginx_base + nginx_notebooks(n_notebooks) + "}"

with open("docker-compose.yml", "w") as f:
    f.write(compose_full)

with open("nginx.conf", "w") as f:
    f.write(nginx_full)
