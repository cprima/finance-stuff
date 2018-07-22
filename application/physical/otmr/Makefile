GOPATH=~/go

.PHONY: all
all: clean test build

update:
	gcloud components update

gae-local:
	GOPATH=$(GOPATH) dev_appserver.py --enable_console --default_gcs_bucket_name GCS_BUCKET_NAME default/app.yaml apicaller/app.yaml


gae-dev:
	cp config_otmrdev ~/.config/gcloud/configurations/config_otmrdev
	gcloud config configurations activate otmrdev
	GOPATH=$(GOPATH) gcloud app deploy default/app.yaml dispatcher/app.yaml apicaller/app.yaml --stop-previous-version --promote --quiet
	gcloud app deploy cron.yaml --quiet
	###gcloud app deploy default/cron.yaml --quiet
	#gcloud app deploy --quiet default/dispatch.yaml 
	#gcloud app deploy --quiet charter/dispatch.yaml
	gcloud app deploy --quiet dispatcher/dispatch.yaml
	#gcloud app deploy --quiet apicaller/dispatch.yaml
	#gcloud app deploy --quiet charter/dispatch.yaml 

	gcloud app deploy --quiet apicaller/queue.yaml

gae:
	cp config_otmrdev ~/.config/gcloud/configurations/config_otmrdev
	gcloud config configurations activate otmrdev
	gcloud app deploy charter/app.yaml --stop-previous-version --promote --quiet
	#GOPATH=$(GOPATH) gcloud app deploy apicaller/app.yaml dispatcher/app.yaml --stop-previous-version --promote --quiet
	#gcloud app deploy --quiet dispatcher/dispatch.yaml
	#gcloud app deploy --quiet apicaller/queue.yaml
	#gcloud app deploy cron.yaml --quiet
