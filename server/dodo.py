import os
from commands import getstatusoutput as gso
import sys
import glob

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
DJANGO_PREAMBLE = 'DJANGO_SETTINGS_MODULE="dri_server.web.settings" '
NOSE_CMD = '%s %s `which nosetests` --exe --with-id ' % (DJANGO_PREAMBLE, PYTHON_EXE)
QUICKTEST_ADDENDUM = " -vv -s --stop"
NGINX_CMD = 'nginx -c /home/peter/work/etc/nginx/nginx.conf -p /home/peter/work/ -g "env prefix=/tmp; env dri_root=/home/peter/work/; error_log loggy;"'

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
        pidfile = '/home/peter/work/var/run/gunicorn/dri_web.pid'
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

def task_config_files():
    "Configures nginx, etc."
    return {
            "actions": [
                        "mkdir -p %s/etc/nginx",
                        "mkdir -p %s/var/log/nginx",
                        "cp ../defaults/nginx.conf %s/etc/nginx" % SYSTEM_ROOT,
                        "cp ../defaults/dri.conf %s/etc/nginx" % SYSTEM_ROOT,
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
            "task_dep": ["install"],
           }


