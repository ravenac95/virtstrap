# Install using the source
install:
	cd virtstrap-core; pip install .
	cd virtstrap; pip install .

# Install an editable version of the source
install-develop:
	cd virtstrap-core/; pip install -e .
	cd virtstrap/; pip install -e .

# Setup the development environment
develop:
	python vstrap.py
	source quickactivate.sh; cd virtstrap-core/; python setup.py develop
	source quickactivate.sh; cd virtstrap/; python setup.py develop
	source quickactivate.sh; cd virtstrap-local/; python setup.py develop

# Runs fast(ish) tests using only the current python environment
quicktest:
	@echo "******************VIRTSTRAP-CORE TESTS*******************"
	@cd virtstrap-core; make ptest
	@echo "******************VIRTSTRAP (MAIN WRAPPER) TESTS*******************"
	@cd virtstrap; make ptest
	@echo "******************VIRTSTRAP-LOCAL TESTS*******************"
	@cd virtstrap-local; make ptest
	@echo "******************HIGH-LEVEL SHELL TESTS*******************"
	@cd tests; sh run_tests

# Test all of the pac
testall: toxtests
	@cd tests; sh run_tests

# Runs all the tox tests
toxtests:
	@echo "******************VIRTSTRAP-CORE TESTS*******************"
	@cd virtstrap-core; tox
	@echo "******************VIRTSTRAP (MAIN WRAPPER) TESTS*******************"
	@cd virtstrap; tox
	@echo "******************VIRTSTRAP-LOCAL TESTS*******************"
	@cd virtstrap-local; tox

# Create support files for the virtstrap package
supportfiles:
	@cd virtstrap; rm virtstrap_support/virtstrap-*
	@cd virtstrap-core; rm -r dist; python setup.py sdist; cp dist/*.tar.gz ../virtstrap/virtstrap_support
	@cd virtstrap-local; rm -r dist; python setup.py sdist; cp dist/*.tar.gz ../virtstrap/virtstrap_support

# Packages and ships to PyPI
distribute:
	@cd virtstrap; python setup.py sdist upload
	@cd virtstrap-core; python setup.py sdist upload
	@cd virtstrap-local; python setup.py sdist upload
