include .env

CURRENT_DATETIME=$(shell date +%Y-%m-%d-%H-%M-%S)

MONGODB_BACKUPS_DIR=backups
MONGODB_DROPDB=docker-compose run mongodb mongo --authenticationDatabase admin -u "${MONGODB_INITDB_ROOT_USERNAME}" -p "${MONGODB_INITDB_ROOT_PASSWORD}" mongodb://mongodb:27017/geekbrains --eval "printjson(db.dropDatabase())"
MONGODB_RESTORE_DATETIME=$(shell basename `find ${MONGODB_BACKUPS_DIR} -maxdepth 1 -type d ! -path ${MONGODB_BACKUPS_DIR} | sort -r | head -1`)
MONGODB_RESTORE_TGZ=$(shell basename `ls -1 ${MONGODB_BACKUPS_DIR}/${MONGODB_RESTORE_DATETIME}/*.tgz | head -1`)
MONGODB_RESTORE=docker-compose run mongodb mongorestore --authenticationDatabase admin -u "${MONGODB_INITDB_ROOT_USERNAME}" -p "${MONGODB_INITDB_ROOT_PASSWORD}" --host mongodb --port 27017 --db geekbrains --verbose /var/backups/${MONGODB_RESTORE_DATETIME}/geekbrains/
MONGODB_BACKUP_MKDIR=docker-compose run mongodb mkdir -m 777 /var/backups/${CURRENT_DATETIME}
MONGODB_BACKUP=docker-compose run mongodb mongodump --authenticationDatabase admin -u "${MONGODB_INITDB_ROOT_USERNAME}" -p "${MONGODB_INITDB_ROOT_PASSWORD}" --db geekbrains --host mongodb --port 27017 --out /var/backups/${CURRENT_DATETIME}/
MONGODB_SHELL=docker-compose run mongodb mongo --authenticationDatabase admin -u "${MONGODB_INITDB_ROOT_USERNAME}" -p "${MONGODB_INITDB_ROOT_PASSWORD}" mongodb://mongodb:27017/geekbrains

env ?= dev
ver ?= latest

HELP_FUN = \
		%help; \
		while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^(\w+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/ }; \
		print "usage: make [target]\n\n"; \
	for (keys %help) { \
		print "$$_:\n"; $$sep = " " x (20 - length $$_->[0]); \
		print "  $$_->[0]$$sep$$_->[1]\n" for @{$$help{$$_}}; \
		print "\n"; }

help:           ##@miscellaneous Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

up: ## Starts the app
	docker-compose up -d
	docker-compose ps

down: ## Stops the app
	docker-compose stop

start: up ## Alias to up

stop: down ## Alias to down

restart: stop start ## Restart app

backup: ## Backups the app
	@echo "Backup to "${MONGODB_BACKUPS_DIR}/${CURRENT_DATETIME}
	${MONGODB_BACKUP_MKDIR}
	${MONGODB_BACKUP}
	@echo "Done"

restore: ## Restores the app
	@echo "Restoring from "${MONGODB_RESTORE}
	${MONGODB_DROPDB}
	${MONGODB_RESTORE}
	@echo "Done"

mongodb: ## Mongodb shell
	${MONGODB_SHELL}
