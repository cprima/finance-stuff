GOPATH=~/go

.PHONY: all
all: clean test build


gae-local:
	dev_appserver.py app.yaml


gae-dev:
	cp config_otmrdev ~/.config/gcloud/configurations/config_otmrdev
	gcloud config configurations activate otmrdev
	#GOPATH=$(GOPATH) gcloud app deploy app.yaml --stop-previous-version --promote --quiet #--verbosity=info #--no-promote --promote
	GOPATH=$(GOPATH) gcloud app deploy default/app.yaml dispatcher/app.yaml apicaller/app.yaml --stop-previous-version --promote --quiet
	GOPATH=$(GOPATH) gcloud app deploy default/cron.yaml --quiet