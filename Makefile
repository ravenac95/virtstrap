getsubs:
	git submodule init
	git submodule update

environment:
	python vstrap.py
	source quickactivate.sh; cd virtstrap-core/; python setup.py develop
	source quickactivate.sh; cd virtstrap/; python setup.py develop
	source quickactivate.sh; cd virtstrap-local/; python setup.py develop

develop:
	make getsubs
	make environment

testall:
	@echo "******************VIRTSTRAP-CORE TESTS*******************"
	cd virtstrap-core; make ptest
	@echo "******************VIRTSTRAP (MAIN WRAPPER) TESTS*******************"
	cd virtstrap; make ptest
