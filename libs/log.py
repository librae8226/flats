import logging

# create logger
log = logging.getLogger('flats')
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
log.addHandler(ch)

# 'application' code
#log.debug('debug message')
#log.info('info message')
#log.warn('warn message')
#log.error('error message')
#log.critical('critical message')
