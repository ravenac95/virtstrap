getsubs:
	git submodule init
	git submodule update

environment:
	python vstrap.py
	source quickactivate.sh; cd virtstrap-core/; python setup.py develop
	source quickactivate.sh; cd virtstrap/; python setup.py develop
	source quickactivate.sh; cd virtstrap-local/; python setup.py develop
