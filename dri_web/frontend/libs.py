import logging
import pprint

def log_object(object, title='', max_lines=0):
    "Sometimes you just have to log an entire object out"
    logger = logging.getLogger('dri.custom')
    if title:
        logger.info(title.upper().ljust(50,'-'))
    current_line = 0
    for line in pprint.pformat(object).split('\n'):
        logger.info(">> %s" % line)
        current_line += 1
        if max_lines:
            if current_line > max_lines:
                break
    if title:
        logger.info(title.upper().ljust(50,'='))

