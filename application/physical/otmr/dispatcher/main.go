package main

import (
	"fmt"
	"net/http"

	"google.golang.org/appengine"
)

func main() {
	http.HandleFunc("/dispatcher", handleDispatcher)
	http.HandleFunc("/", handle)
	appengine.Main()
}

func handleDispatcher(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "otmr-dev-dispatcher-v1/dispatcher")
}

func handle(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "otmr-dev-dispatcher-v1")
}
