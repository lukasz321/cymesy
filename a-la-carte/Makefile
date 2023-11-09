CURRENT_DIR := ${CURDIR}

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MKFILE_DIR := $(dir $(MKFILE_PATH))

.PHONY: all
all: | misc pkg 

.PHONY: install
install: | pkg

.PHONY: git
git:
	git fetch
	git pull
	git submodule init
	git submodule update

.PHONY: misc
misc:
	USER=$(whoami)
	sudo adduser $(USER) dialout
	sudo adduser $(USER) root
	sudo mkdir -p /var/lock
	chmod 600 /var/lock

.PHONY: pkg
pkg:
	cd $(MKFILE_DIR) && sudo python3 setup.py install
