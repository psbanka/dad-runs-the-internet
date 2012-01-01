"Information about this module, used in building."
COMPONENT_INFO = {
"scripts": [ "scripts/dri.wsgi"],
"data_files":
[
["share/dri-templates", [
    "share/dri-templates/404.html",
]],
["share/dri-templates/css", [
    "share/dri-templates/css/frontpage.css",
]],
["share/dri-templates/js", [
    "share/dri-templates/js/frontpage.js",
]],
["share/dri-templates/frontend", [
    "share/dri-templates/frontend/index.html",
    "share/dri-templates/frontend/edit_device_form.html",
]],
],
"install_requires": [ "PyYAML", "Pyro", "Django", "pysqlite", 'django-rest-framework', 'django-auth-ldap'],
"rpm_requires": [
    'python',
    'python_dri-Django',
    'python_dri-django-auth-ldap',
    'python_dri-djangorestframework',
    'python_dri-Pyro',
    'PyYAML',
    'dri_core',
],
"vendor_requires": ['pyro', 'django', 'django-auth-ldap', 'django-rest-framework'],
"description": 'DRI web server',
"name": "dri_server",
"package_data": { "dri_server": [ "share/dri-templates/*.html",]
                },
"package_dir": { "dri_server": "src" },
"packages": [
             "dri_server",
             "dri_server.web",
             "dri_server.web.frontend",
            ],
"provides": ["dri_server"]
}
