template = """
server {
    listen   8080;
    server_name sparky;
    # no security problem here, since / is alway passed to upstream
    root /dojango/test/;
    # serve directly - analogous for static/staticfiles
    location /media/ {
        # if asset versioning is used
        if ($query_string) {
            expires max;
        }
    }
    location /static/admin/ {
        root %(system_root)s/lib/python2.7/site-packages/Django-1.3.1-py2.7.egg/django/contrib;
    }
    location /js {
        root %(system_root)s/share/dri-templates/;
    }
    location /css {
        root %(system_root)s/share/dri-templates/;
    }
    location / {
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 10;
        proxy_read_timeout 10;
        proxy_pass http://localhost:8000/;
    }
    # what to serve if upstream is not available or crashes
    error_page 500 502 503 504 /media/50x.html;
}
"""
