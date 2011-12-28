import os

SYSTEM_ROOT = os.environ.get("VIRTUAL_ENV", '/')
HTTPD_PATH = os.path.join(SYSTEM_ROOT, 'etc', 'httpd')
COMPONENTS = ['server']
VAR_RUN = os.path.join(SYSTEM_ROOT, "var", "run")
HTTPD_PATH = os.path.join(SYSTEM_ROOT, 'etc', 'httpd')
DEWIT = "python $(which doit)"

def _make_link(source, dest):
    if not os.path.islink(dest):
        os.system('ln -s %s %s' % (source, dest))

def configure_apache():
    os.system('mkdir -p %s/conf' % HTTPD_PATH)
    os.system('mkdir -p %s/conf.d' % HTTPD_PATH)
    os.system('mkdir -p %s/var/log/httpd' % SYSTEM_ROOT)
    os.system('mkdir -p %s/var/run/httpd' % SYSTEM_ROOT)
    _make_link("%s/var/log/httpd" % SYSTEM_ROOT,  "%s/logs" % HTTPD_PATH)
    _make_link("%s/var/run/httpd" % SYSTEM_ROOT,  "%s/run" % HTTPD_PATH)
    _make_link("/usr/lib64/httpd/modules", "%s/modules" % (HTTPD_PATH))
    os.system('cp ../defaults/httpd.conf %s/conf' % HTTPD_PATH)
    os.system('cp ../defaults/tnt.conf %s/conf.d/tnt.conf' % HTTPD_PATH)
    os.environ["DRI_ROOT"] = SYSTEM_ROOT
    os.system('export DRI_ROOT="%s"' % SYSTEM_ROOT)

def server_command(command, quiet = False):
    cmd = "echo 'running daemon...'"
    if quiet:
        cmd += "> /dev/null"
    os.system(cmd)
    os.system("httpd -d %s -k %s" % (HTTPD_PATH, command))

def assure_virtual():
    "make sure we're in a virtual environment"
    if os.environ.get("VIRTUAL_ENV"):
        return True
    return False

def task_set_config_data():
    "Sets the data in /etc/tnt/server.yml"
    return {
            #"targets": ["/var/deploy/rest_api"],
            "actions": [(configure_apache,)],
            "task_dep": ["cleanup"],
           }

def task_setup_fixtures():
    "Does nothing at the moment"
    return {"actions": []}

def task_devstart():
    "Start the test server"
    return {"actions": [(server_command, ["start"]),],
            "task_dep": ["install_everything:" + c for c in COMPONENTS] + \
                        ["set_config_data", "setup_fixtures"],
            "verbosity": 2,
           }

def task_install_everything():
    "Deploy all the components and test"
    for component in COMPONENTS:
        yield {
                "name": component,
                "actions": [
                            (assure_virtual,),
                            "cd ../%s && %s install" % (component, DEWIT),
                           ],
              }

def task_cleanup():
    "Clean out old builds"
    def rmrf(filename):
        return "rm -rf %s" % filename

    return {"actions": [(server_command, ['stop'], {"quiet":"true"}),
                        'rm -rf %s/*.pid' % VAR_RUN,
                       ],
           }

