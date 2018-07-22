package main

//todo https://stackoverflow.com/questions/21108084/golang-mysql-insert-multiple-data-at-once

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"strings"

	"cloud.google.com/go/storage"
	"google.golang.org/api/iterator"
	"google.golang.org/appengine"
	"google.golang.org/appengine/file"
	"google.golang.org/appengine/log"
	"google.golang.org/appengine/taskqueue"
	"google.golang.org/appengine/urlfetch"
)

func main() {

	http.HandleFunc("/apicaller", handleApicaller)
	http.HandleFunc("/av/", handleAlphavantage)
	//http.HandleFunc("/v1/alphavantage/TIME_SERIES_DAILY_ADJUSTED/^GDAXI", handleApicaller)
	http.HandleFunc("/", handle)
	appengine.Main()
}

func handleAlphavantage(w http.ResponseWriter, r *http.Request) {
	ctx := appengine.NewContext(r)
	function := strings.Split(strings.TrimPrefix(r.URL.Path, "/av/"), "/")[0]
	symbol := strings.Split(strings.TrimPrefix(r.URL.Path, "/av/"), "/")[1]
	log.Infof(ctx, "Called with function: %v symbol: %v", function, symbol)

	apikey := os.Getenv("ALPHAVANTAGEAPIKEY")
	myurl := fmt.Sprintf("https://www.alphavantage.co/query?function=%v&symbol=%v&apikey=%v", function, symbol, apikey)
	fmt.Fprintf(w, "Called with\nfunction: %v\nsymbol: %v\nfor url %v", function, symbol, myurl)
	client := urlfetch.Client(ctx)

	resp, err := client.Get(myurl)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "HTTP GET returned status %v", resp.Status)
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err.Error())
	}
	//fmt.Fprintln(w, body)

	bucket, err := file.DefaultBucketName(ctx)
	if err != nil {
		log.Errorf(ctx, "failed to get default GCS bucket name: %v", err)
	}
	fmt.Fprintln(w, "bucket:"+bucket)

	client2, err := storage.NewClient(ctx)
	if err != nil {
		log.Errorf(ctx, "failed to create client: %v", err)
		return
	}
	defer client2.Close()

	buf := &bytes.Buffer{}
	d := &demo{
		w:          buf,
		ctx:        ctx,
		client:     client2,
		bucket:     client2.Bucket(bucket),
		bucketName: bucket,
	}
	//fmt.Sprintf("%c", '^')
	//tmp := strings.Replace(symbol, "^", "-", -1)
	//n := "av_" + function + "_" + strings.Replace(symbol, "^", "", -1) + ".json"

	d.createFilePublic("av_"+function+"_"+strings.Replace(symbol, "^", "", -1)+".json", body, appengine.AppID(ctx))

	task := taskqueue.NewPOSTTask("/mpl/"+strings.Replace(symbol, "^", "", -1), url.Values{})
	_, err = taskqueue.Add(ctx, task, "candlestick")
	if err != nil {
		// Handle error
	}
}

func handleApicaller(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "otmr-dev-apicaller-v1/apicaller")

	//url := "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=^GDAXI&apikey="
	url := "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=demo"
	ctx := appengine.NewContext(r)
	client := urlfetch.Client(ctx)
	resp, err := client.Get(url)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprintf(w, "HTTP GET returned status %v", resp.Status)
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err.Error())
	}
	fmt.Fprintln(w, body)

	bucket, err := file.DefaultBucketName(ctx)
	if err != nil {
		log.Errorf(ctx, "failed to get default GCS bucket name: %v", err)
	}
	fmt.Fprintln(w, "bucket:"+bucket)

	client2, err := storage.NewClient(ctx)
	if err != nil {
		log.Errorf(ctx, "failed to create client: %v", err)
		return
	}
	defer client2.Close()

	buf := &bytes.Buffer{}
	d := &demo{
		w:          buf,
		ctx:        ctx,
		client:     client2,
		bucket:     client2.Bucket(bucket),
		bucketName: bucket,
	}
	n := "demo-testfile-go"
	d.createFile(n, body)

}

func handle(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "otmr-dev-apicaller-v1")
}

// demo struct holds information needed to run the various demo functions.
type demo struct {
	client     *storage.Client
	bucketName string
	bucket     *storage.BucketHandle

	w   io.Writer
	ctx context.Context
	// cleanUp is a list of filenames that need cleaning up at the end of the demo.
	cleanUp []string
	// failed indicates that one or more of the demo steps failed.
	failed bool
}

func (d *demo) errorf(format string, args ...interface{}) {
	d.failed = true
	fmt.Fprintln(d.w, fmt.Sprintf(format, args...))
	log.Errorf(d.ctx, format, args...)
}
func (d *demo) dumpStats(obj *storage.ObjectAttrs) {
	fmt.Fprintf(d.w, "(filename: /%v/%v, ", obj.Bucket, obj.Name)
	fmt.Fprintf(d.w, "ContentType: %q, ", obj.ContentType)
	fmt.Fprintf(d.w, "ACL: %#v, ", obj.ACL)
	fmt.Fprintf(d.w, "Owner: %v, ", obj.Owner)
	fmt.Fprintf(d.w, "ContentEncoding: %q, ", obj.ContentEncoding)
	fmt.Fprintf(d.w, "Size: %v, ", obj.Size)
	fmt.Fprintf(d.w, "MD5: %q, ", obj.MD5)
	fmt.Fprintf(d.w, "CRC32C: %q, ", obj.CRC32C)
	fmt.Fprintf(d.w, "Metadata: %#v, ", obj.Metadata)
	fmt.Fprintf(d.w, "MediaLink: %q, ", obj.MediaLink)
	fmt.Fprintf(d.w, "StorageClass: %q, ", obj.StorageClass)
	if !obj.Deleted.IsZero() {
		fmt.Fprintf(d.w, "Deleted: %v, ", obj.Deleted)
	}
	fmt.Fprintf(d.w, "Updated: %v)\n", obj.Updated)
}

// listBucket lists the contents of a bucket in Google Cloud Storage.
func (d *demo) listBucket() {
	io.WriteString(d.w, "\nListbucket result:\n")

	query := &storage.Query{Prefix: "foo"}
	it := d.bucket.Objects(d.ctx, query)
	for {
		obj, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			d.errorf("listBucket: unable to list bucket %q: %v", d.bucketName, err)
			return
		}
		d.dumpStats(obj)
	}
}

// createFile creates a file in Google Cloud Storage.
func (d *demo) createFile(fileName string, body []byte) {
	fmt.Fprintf(d.w, "Creating file /%v/%v\n", d.bucketName, fileName)

	wc := d.bucket.Object(fileName).NewWriter(d.ctx)
	wc.ContentType = "text/plain"
	wc.Metadata = map[string]string{
		"x-goog-meta-foo": "foo",
		"x-goog-meta-bar": "bar",
	}
	d.cleanUp = append(d.cleanUp, fileName)

	if _, err := wc.Write(body); err != nil {
		d.errorf("createFile: unable to write data to bucket %q, file %q: %v", d.bucketName, fileName, err)
		return
	}
	if err := wc.Close(); err != nil {
		d.errorf("createFile: unable to close bucket %q, file %q: %v", d.bucketName, fileName, err)
		return
	}
}

// createFile creates a file in Google Cloud Storage.
func (d *demo) createFilePublic(fileName string, body []byte, ProjectNumber string) {
	fmt.Fprintf(d.w, "Creating file /%v/%v\n", d.bucketName, fileName)

	wc := d.bucket.Object(fileName).NewWriter(d.ctx)
	wc.ContentType = "text/plain"
	wc.Metadata = map[string]string{
		"x-goog-meta-foo": "foo",
		"x-goog-meta-bar": "bar",
	}
	//https://github.com/GoogleCloudPlatform/google-cloud-go/issues/122
	wc.ACL = []storage.ACLRule{
		{Entity: storage.AllUsers, Role: storage.RoleReader},
		{Entity: storage.ACLEntity("project-owners-" + ProjectNumber), Role: storage.RoleOwner},
		{Entity: storage.ACLEntity("project-editors-" + ProjectNumber), Role: storage.RoleOwner},
		{Entity: storage.ACLEntity("project-viewers-" + ProjectNumber), Role: storage.RoleOwner},
	}
	d.cleanUp = append(d.cleanUp, fileName)

	if _, err := wc.Write(body); err != nil {
		d.errorf("createFile: unable to write data to bucket %q, file %q: %v", d.bucketName, fileName, err)
		return
	}
	if err := wc.Close(); err != nil {
		d.errorf("createFile: unable to close bucket %q, file %q: %v", d.bucketName, fileName, err)
		return
	}
}
