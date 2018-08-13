package main

import (
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/rickar/cal"
	"google.golang.org/appengine"
	"google.golang.org/appengine/log"
	"google.golang.org/appengine/urlfetch"
)

//Index holds basic info about an index at its leading stock exchange
type Index struct {
	Name   string
	Symbol string
}

//Exchange holds the common abbreviation of a stock exchange and a slice of indices originating there.
type Exchange struct {
	Name     string
	Calendar string
	Indices  []Index
}

var (
	exchanges []Exchange
	endpoint  string
)

func main() {
	http.HandleFunc("/exchange/", handleExchanges)
	http.HandleFunc("/", handle)
	appengine.Main()
}

func handle(w http.ResponseWriter, r *http.Request) {
	ctx := appengine.NewContext(r)
	log.Infof(ctx, "handle func in dispatcher")
	fmt.Fprintln(w, "dispatcher")
}

//handleExchange responds to an API call for a single exchange and
//issues an internal API call to fetch current data in json format
func handleExchanges(w http.ResponseWriter, r *http.Request) {

	exchange := strings.Split(strings.TrimPrefix(r.URL.Path, "/exchange/"), "/")[0]
	//exchanges := getAllExchanges()

	foo, err := getExchange(exchange)
	if err != nil {
		fmt.Fprintln(w, err)
	}
	//fmt.Fprintf(w, "Calendar is %v\n", foo.Calendar)
	c := cal.NewCalendar()
	if foo.Calendar == "de" {
		cal.AddGermanHolidays(c)
		cal.AddEcbHolidays(c)
	} else if foo.Calendar == "us" {
		cal.AddUsHolidays(c)
	}
	t := time.Now()

	if c.IsWorkday(t) {
		ctx := appengine.NewContext(r)
		endpoint = getEndpoint(appengine.ModuleName(ctx), appengine.AppID(ctx))
		client := urlfetch.Client(ctx)

		//http://localhost:8080/exchange/foo?bar=baz
		//tmp := r.URL.Query()["bar"][0] //will be bar
		//r.URL.Path // will be /exchange/foo

		for _, index := range foo.Indices {
			//https://stackoverflow.com/a/13826910/9576512
			var URL *url.URL
			URL, _ = url.Parse(getEndpoint(appengine.ModuleName(ctx), appengine.AppID(ctx)) + "TIME_SERIES_DAILY_ADJUSTED/" + index.Symbol)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			_, err := client.Get(URL.String())
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}

			//fmt.Fprintf(w, "HTTP GET returned status %v\n", resp.Status)
		}
	} else {
		fmt.Fprintf(w, "Is not a workday %v\n", "")
	}

	fmt.Fprintln(w, "otmr-dev-dispatcher-v1/exchange")

}

func getAllExchanges() []*Exchange {

	exchanges := []*Exchange{
		&Exchange{
			Name:     "NASDAQ",
			Calendar: "us",
			Indices: []Index{
				Index{
					Name:   "S&P",
					Symbol: "SPX",
				},
			},
		},
		&Exchange{
			Name:     "XETRA",
			Calendar: "de",
			Indices: []Index{
				Index{
					Name:   "DAX",
					Symbol: "^GDAXI",
				},
			},
		},
	}
	return exchanges
}

func getEndpoint(modulename string, appid string) string {
	return "http://" + modulename + "-dot-" + appid + ".appspot.com/av/"
}

func getExchange(exchange string) (*Exchange, error) {
	exchanges := getAllExchanges()
	for _, v := range exchanges {
		if strings.ToLower(v.Name) == strings.ToLower(exchange) {
			return v, nil

		}
	}
	return nil, errors.New("Supplied exchange not found in preconfigured exchanges")
}
