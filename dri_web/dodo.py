import os
from commands import getstatusoutput as gso
import sys

OK = 0
SYSTEM_ROOT = os.environ.get("VIRTUAL_ENV", '/')
HTTPD_PATH = os.path.join(SYSTEM_ROOT, 'etc', 'apache2')
COMPONENTS = ['server']
VAR_RUN = os.path.join(SYSTEM_ROOT, "var", "run")
DEWIT = "python $(which doit)"
PYTHON_EXE = sys.executable
VERSION_TEMPLATE = """\
VERSION_INFO = {
    "Revision": "%s",
}
"""
DB_FILE = "%s/var/lib/dri/web_models.db" % SYSTEM_ROOT
DJANGO_PREAMBLE = 'DJANGO_SETTINGS_MODULE="dri_server.web.settings" '
NOSE_CMD = '%s %s `which nosetests` --exe --with-id ' % (DJANGO_PREAMBLE, PYTHON_EXE)
QUICKTEST_ADDENDUM = " -vv -s --stop"
NGINX_CMD = 'nginx -c %s/etc/nginx/nginx.conf -p %s -g "env prefix=/tmp; env dri_root=%s; error_log loggy;"' % (SYSTEM_ROOT, SYSTEM_ROOT, SYSTEM_ROOT)

##################### EXCEPTIONS

class BuildConfigurationException(Exception):
    "Something is wrong with the build, so throw an exeption"
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return "BuildConfigurationException: %s" % self.msg
    def __repr__(self):
        return self.__str__()

##################### SUPPORT FUNCTIONS

def get_version():
    "Get the SVN revision number for this build"
    status, output = gso("git rev-parse --short HEAD")
    if status != OK:
        raise BuildConfigurationException("Unable to obtain SVN version")
    version_info = output.strip()
    print ">>> (%s)" % version_info
    version_python_code = VERSION_TEMPLATE % version_info
    open("src/_version.py", 'w').write(version_python_code)

def rmrf(filename):
    return "rm -rf %s" % filename

def _make_link(source, dest):
    if not os.path.islink(dest):
        os.system('ln -s %s %s' % (source, dest))

def server_command(command, quiet = False):
    if command == "start":
        cmd = "echo 'running daemon...'"
        if quiet:
            cmd += "> /dev/null"
        cwd = os.getcwd()
        os.system(cmd)
        os.chdir("../defaults")
        os.system("./gunicorn-start.sh")
        os.chdir(cwd)
        cmd = NGINX_CMD
        os.system(cmd)
    else:
        pidfile = '%s/var/run/gunicorn.pid' % SYSTEM_ROOT
        try:
            pid = open(pidfile).read()
            os.system('kill %s' % pid)
            os.system('rm %s' % pidfile)
            cmd = NGINX_CMD + " -s stop"
            os.system(cmd)
        except IOError:
            print "Nothing to kill..."

def task_version():
    "prepare to build"
    return {"actions": [
                        (get_version,),
                       ],
           }

def task_clean_build():
    "Clean out old builds"
    return {"actions": map(rmrf, [
                        "build",
                        "dist",
                        "MANIFEST",
                        "MANIFEST.in",
                        "_manifest_test",
                        "src/_version.py",
                       ]),
           }

def task_syncdb():
    return {
        "actions": [
                    "rm -f %s" % DB_FILE, 
                    "%s python src/web/manage.py syncdb --noinput" % DJANGO_PREAMBLE,
                    "cp -f %s ../defaults/web_models.db" % DB_FILE, 
                   ],
        "task_dep": ['config_files', 'install_everything'],
        "verbosity": 2,
    }

def _create_config_file(template_name, dest_name):
    sys.path.append("%s/dri" % SYSTEM_ROOT)
    module_name = 'defaults.%s' % template_name
    template = ""
    import_cmd = "from %s import template" % module_name
    exec(import_cmd)
    config_data = template % {'system_root': SYSTEM_ROOT}
    open("%s/%s" % (SYSTEM_ROOT, dest_name), 'w').write(config_data)

def task_config_files():
    "Configures nginx, etc."
    return {
            "actions": [
                        "mkdir -p %s/var/run" % SYSTEM_ROOT,
                        "mkdir -p %s/etc/nginx" % SYSTEM_ROOT,
                        "mkdir -p %s/var/log/nginx" % SYSTEM_ROOT,
                        "mkdir -p %s/var/lib/dri/media" % SYSTEM_ROOT,
                        "touch %s/var/log/nginx/error.log" % SYSTEM_ROOT,
                        "touch %s/var/log/gunicorn.log" % SYSTEM_ROOT,
                        "touch %s/var/run/nginx.pid" % SYSTEM_ROOT,
                        (_create_config_file, ("nginx_template", "/etc/nginx/nginx.conf")),
                        (_create_config_file, ("dri_conf_template", "/etc/nginx/dri.conf")),
                        "cp ../defaults/web_models.db %s/var/lib/dri" % SYSTEM_ROOT,
                        #"cp ../defaults/nginx.conf %s/etc/nginx" % SYSTEM_ROOT,
                        #"cp ../defaults/dri.conf %s/etc/nginx" % SYSTEM_ROOT,
                       ]
           }

def task_build():
    "Builds the code"
    return {"actions": [
                        "%s setup.py build" % PYTHON_EXE,
                       ],
            "task_dep": ["clean_build", "version"],
           }

def assure_virtual():
    "make sure we're in a virtual environment"
    if os.environ.get("VIRTUAL_ENV"):
        return True
    return False

def task_setup_fixtures():
    "Does nothing at the moment"
    return {"actions": []}

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

def task_stop():
    "Stop the test server"
    return {"actions": [(server_command, ["stop"]),]}

def task_start():
    "Start the test server"
    return {"actions": [(server_command, ["start"]),],
            "task_dep": ["install_everything:" + c for c in COMPONENTS] + \
                        ["setup_fixtures", "config_files"],
            "verbosity": 2,
           }

def task_restart():
    "Start the test server"
    return {"actions": [],
            "task_dep": ["stop", "start"],
            "verbosity": 2,
           }

def task_install():
    "Install the code."
    return {"actions": [
                        "%s setup.py install" % PYTHON_EXE,
                       ],
            "task_dep": ["build"],
           }

def task_quicktest():
    "Run quick unit tests without any of the other nonsense."
    def quicktest(test_id):
        cmd = "%s %s %s" % (NOSE_CMD, test_id, QUICKTEST_ADDENDUM)
        print '-------------------------------------------------------'
        print "Here's the command: %s" % cmd
        print '-------------------------------------------------------'
        os.system(cmd)

    return {
            "actions": [(quicktest,)],
            "params": [{
                        'name': 'test_id',
                        'short': 'i',
                        'default': '',
                       }],
            "verbosity": 2,
            "task_dep": ["install", "config_files"],
           }


