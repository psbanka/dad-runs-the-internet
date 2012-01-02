#!/bin/bash
set -e
LOGFILE=$VIRTUAL_ENV/var/log/gunicorn.log
PIDFILE=$VIRTUAL_ENV/var/run/gunicorn.pid
echo "logging to: " $LOGFILE
LOGDIR=$(dirname $LOGFILE)
PIDDIR=$(dirname $PIDFILE)
#kill $(cat $PIDFILE 2>/dev/null) 2>/dev/null || echo 'no killing'
#echo "---------------"
NUM_WORKERS=1
# user/group to run as
USER=peter
GROUP=peter
DJANGO_SETTINGS_MODULE="dri_server.web.settings" 
export DJANGO_SETTINGS_MODULE
cd $VIRTUAL_ENV/dri

test -d $LOGDIR || mkdir -p $LOGDIR
test -d $PIDDIR || mkdir -p $PIDDIR
exec $VIRTUAL_ENV/bin/gunicorn_django -w $NUM_WORKERS \
  --log-level=debug \
  --log-file=$LOGFILE --pid=$PIDFILE -D
