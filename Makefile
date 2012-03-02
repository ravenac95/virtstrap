# Get and update the submodules
getsubs:
	git submodule init
	git submodule update

# Install using the source
install:
	make getsubs
	cd virtstrap-core; pip install .
	cd virtstrap; pip install .

# Install an editable version of the source
install-develop:
	make getsubs
	cd virtstrap-core/; pip install -e .
	cd virtstrap/; pip install -e .

# Setup the development environment
environment:
	python vstrap.py
	source quickactivate.sh; cd virtstrap-core/; python setup.py develop
	source quickactivate.sh; cd virtstrap/; python setup.py develop
	source quickactivate.sh; cd virtstrap-local/; python setup.py develop

# Quickstart for developers
develop:
	make getsubs
	make environment

# Test all of the packages
testall:
	@echo "******************VIRTSTRAP-CORE TESTS*******************"
	@cd virtstrap-core; make ptest
	@echo "******************VIRTSTRAP (MAIN WRAPPER) TESTS*******************"
	@cd virtstrap; make ptest
	@echo "******************VIRTSTRAP-LOCAL TESTS*******************"
	@cd virtstrap-local; make ptest

# Create support files for the virtstrap package
supportfiles:
	cd virtstrap-core; python setup.py sdist; cp dist/*.tar.gz ../virtstrap/virtstrap_support
	cd virtstrap-local; python setup.py sdist; cp dist/*.tar.gz ../virtstrap/virtstrap_support
