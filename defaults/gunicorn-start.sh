#!/bin/bash
set -e
LOGFILE=$DRI_ROOT/var/log/gunicorn/dri_web.log
PIDFILE=$DRI_ROOT/var/run/gunicorn/dri_web.pid
echo "logging to: " $LOGFILE
LOGDIR=$(dirname $LOGFILE)
PIDDIR=$(dirname $PIDFILE)
kill $(cat $PIDFILE) >/dev/null || echo 'no killing'
echo "---------------"
NUM_WORKERS=1
# user/group to run as
USER=peter
GROUP=peter
DJANGO_SETTINGS_MODULE="dri_server.web.settings" 
export DJANGO_SETTINGS_MODULE
cd /home/peter/work/dri

test -d $LOGDIR || mkdir -p $LOGDIR
test -d $PIDDIR || mkdir -p $PIDDIR
exec ../bin/gunicorn_django -w $NUM_WORKERS \
  --log-level=debug \
  --log-file=$LOGFILE -D --pid=$PIDFILE
