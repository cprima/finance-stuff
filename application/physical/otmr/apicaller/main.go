package main

import (
	"fmt"
	"net/http"

	"google.golang.org/appengine"
)

func main() {
	http.HandleFunc("/apicaller", handleApicaller)
	http.HandleFunc("/", handle)
	appengine.Main()
}

func handleApicaller(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "otmr-dev-apicaller-v1/apicaller")
}

func handle(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "otmr-dev-apicaller-v1")
}
