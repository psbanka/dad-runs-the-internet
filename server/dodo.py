import os
from commands import getstatusoutput as gso
import sys

OK = 0
SYSTEM_ROOT = os.environ.get("VIRTUAL_ENV", '/')
HTTPD_PATH = os.path.join(SYSTEM_ROOT, 'etc', 'httpd')
COMPONENTS = ['server']
VAR_RUN = os.path.join(SYSTEM_ROOT, "var", "run")
HTTPD_PATH = os.path.join(SYSTEM_ROOT, 'etc', 'httpd')
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

def configure_apache():
    os.system('mkdir -p %s/conf' % HTTPD_PATH)
    os.system('mkdir -p %s/conf.d' % HTTPD_PATH)
    os.system('mkdir -p %s/var/log/httpd' % SYSTEM_ROOT)
    os.system('mkdir -p %s/var/run/httpd' % SYSTEM_ROOT)
    _make_link("%s/var/log/httpd" % SYSTEM_ROOT,  "%s/logs" % HTTPD_PATH)
    _make_link("%s/var/run/httpd" % SYSTEM_ROOT,  "%s/run" % HTTPD_PATH)
    _make_link("/usr/lib64/httpd/modules", "%s/modules" % (HTTPD_PATH))
    #os.system('cp ../defaults/httpd.conf %s/conf' % HTTPD_PATH)
    os.system('cp ../dri.conf %s/conf.d/dri.conf' % HTTPD_PATH)
    os.environ["DRI_ROOT"] = SYSTEM_ROOT
    os.system('export DRI_ROOT="%s"' % SYSTEM_ROOT)

def server_command(command, quiet = False):
    cmd = "echo 'running daemon...'"
    if quiet:
        cmd += "> /dev/null"
    os.system(cmd)
    os.system("httpd -d %s -k %s" % (HTTPD_PATH, command))

def task_version():
    "prepare to build"
    return {"actions": [
                        #(get_file, ["_project_info.py"]),
                        #(get_file, ["setup.py"]),
                        #"cp _project_info.py src",
                        (get_version,),
                       ],
           }

def task_clean_build():
    "Clean out old builds"
    def rmrf(filename):
        return "rm -rf %s" % filename

    return {"actions": map(rmrf, [
                        "build",
                        "dist",
                        "MANIFEST",
                        "MANIFEST.in",
                        "_manifest_test",
                        #"_project_info.py",
                        #"setup.py",
                        #"src/_project_info.py",
                        "src/_version.py",
                        #"testdb",
                       ]),
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

def task_set_config_data():
    "Sets up configuration data"
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
            "task_dep": ["install", "set_config_data"],
           }


