"Information about this module, used in building."
COMPONENT_INFO = {
"scripts": [ "scripts/dri.wsgi"],
"data_files":
[
["share/dri-templates", [
    "share/dri-templates/404.html",
]],
["share/dri-templates/html_files", [
    "share/dri-templates/html_files/base.html",
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
"name": "dri_web",
"package_data": { "dri_web": [ "share/dri-templates/*.html",]
                },
"package_dir": { "dri_web": "src" },
"packages": [
             "dri_web",
             "dri_web.web",
            ],
"provides": ["dri_web"]
}
