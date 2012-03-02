test:
	nosetests -d

# THIS TEST ONLY WORK ON OSX as far as I know
# It defaults to having a timeout of 30 seconds
ptest: 
	nosetests -d --processes=8 --process-timeout=30

# Verbose parallel testing
ptestv: 
	nosetests -d --processes=8 --process-timeout=30 -v

quicktest:
	nosetests -a '!slow' -d

# Verbose quick tests
quicktestv:
	nosetests -a '!slow' -d -v
