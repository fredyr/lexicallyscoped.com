---
layout: post
title: Parsing fixed-width flat files with Clojure

---

### Fixed-width flat files! 

Have you seen files like these?

{% highlight text %}
01AUTOGIRO              20091110193055123456BET. SPEC & STOPP TK4711170009912346
82200911100    00000000000001010000003000000009912346000000RIDLEKTION          0
82200911105006 000000000000010200000030000000099123460000000FAKTNR156          0
82200911105006 000000000000010300000030000000099123460000000FAKTNR157          0
32200911100    000000000000011100000010000000099123460000000FAKTNR153          0
32200911100    000000003333102200000010000000099123460000000FAKTNR151          1
{% endhighlight %}

### Application Integration

This particular file is an example file for the Swedish direct debit
transaction reports. Each row is fixed 80 characters long. Previously
when I've worked with application integration between banks and ERP
systems, I've often encountered these types of files. It is quite
handy to be able to parse them, either completely or just extract
relevant information, and send on further into another system. 

### Data parsing in Clojure

All the code presented here, can also be found in the following [gist](https://gist.github.com/fredyr/27b2b476858bda4c4302).

I'd like to show you how you can use Clojure for parsing files like
these, if you were to encounter them.

We'll start by describing our parsing rules. The rules are stored in a
separate file, as plain Clojure data.

A rule book is a set of rules, each describing a specific row
in the flat file. It has

- an identification part, a set of identifiers that uniquely
identifies the record
- a description of the segments we wish to
parse from the record.

The identifiers and segments both are described
by

- an id
- the start position in the row
- the end position in the row.

In addition, for each segment we have the possibility
to include a data type annotation. This will enable us to later on parse the
fields into more useful data types.

Let's have a look at some rules for a subset of the data in our direct
debit example from above:

{% highlight clojure %}
[{:id "opening-record"
  :identifiers [{:start-pos 1 :end-pos 2 :id-string "01"}
                {:start-pos 3 :end-pos 10 :id-string "AUTOGIRO"}
                {:start-pos 45 :end-pos 64 :id-string "BET. SPEC & STOPP TK"}]
  :segments [{:id "datetime-written" :start-pos 25 :end-pos 38 :data-type :datetime}
             {:id "customer-number" :start-pos 65 :end-pos 70 :data-type :long}
             {:id "account" :start-pos 71 :end-pos 80 :data-type :long}]}
 
 {:id "debit"
  :identifiers [{:start-pos 1 :end-pos 2 :id-string "82"}]
  :segments [{:id "payment-date" :start-pos 3 :end-pos 10 :data-type :date}
             {:id "payer-id" :start-pos 16 :end-pos 31}
             {:id "amount" :start-pos 32 :end-pos 43 :data-type :amount}
             {:id "payment-reference" :start-pos 54 :end-pos 69}
             {:id "status" :start-pos 80 :end-pos 80 :data-type :long}]}
 {:id "credit"
  :identifiers [{:start-pos 1 :end-pos 2 :id-string "32"}]
  :segments [{:id "payment-date" :start-pos 3 :end-pos 10 :data-type :date}
             {:id "payer-id" :start-pos 16 :end-pos 31}
             {:id "amount" :start-pos 32 :end-pos 43 :data-type :amount}
             {:id "payment-reference" :start-pos 54 :end-pos 69}
             {:id "status" :start-pos 80 :end-pos 80 :data-type :long}]}] 
{% endhighlight %}

We load the rule books from file, and use the Clojure reader to get
the data structure. In our case, a vector of rules, each being a
hash-map.

{% highlight clojure %}
(defn load-rulebook [file] 
  (with-open [r (reader file)]
    (read (PushbackReader. r))))
{% endhighlight %}

We'll need a couple of helper functions, taking care of the
ground work.

`extract-str` takes a String and a segment definition and parses the
substring defined from the start to the end position:

{% highlight clojure %}
(defn extract-str [s segment]
  (let [start (:start-pos segment)
        end (:end-pos segment)]
    (subs s (dec start) end)))
{% endhighlight %}

To match a rule, all of the identifiers needs to be matched:

{% highlight clojure %}
(defn match-identifier? [row ident]
  (let [s (extract-str row ident)]
    (= s (:id-string ident))))

(defn match-rule? [row idents]
    (every? #(match-identifier? row %) idents))
{% endhighlight %}

To keep it simple, we do a simple linear search to find a matching
rule, by testing them in order

{% highlight clojure %}
(defn find-rule [row rules]
  (first (filter #(match-rule? row (:identifiers %)) rules)))
{% endhighlight %}

Once we've found a match based on our identifiers, we parse the row
using the segments description

{% highlight clojure %}
(defn parse-with-rule [row rule]
  (let [segs (:segments rule)
        extracted (reduce #(assoc %1 (keyword (:id %2)) (extract-str row %2)) {} segs)]
    (assoc extracted :id (:id rule))))

(defn parse-file [file rules]
  (with-open [r (reader file)]
    (doall
      (map #(parse-with-rule % (find-rule % rules)) (line-seq r)))))
{% endhighlight %}

We can now test it with something like:

{% highlight clojure %}
(parse-file "data/dd.txt" (load-rulebook "rules/dd.clj"))

({:id "opening-record", :account "0009912346", :customer-number "471117", :datetime-written "20091110193055"}
 {:id "debit", :status "0", :payment-reference "000000RIDLEKTION",
  :amount "000000300000", :payer-id "0000000000000101", :payment-date "20091110"}
 {:id "debit", :status "0", :payment-reference "0000000FAKTNR156",
  :amount "000000300000", :payer-id "0000000000000102", :payment-date "20091110"}
 {:id "debit", :status "0", :payment-reference "0000000FAKTNR157",
  :amount "000000300000", :payer-id "0000000000000103", :payment-date "20091110"}
 {:id "credit", :status "0", :payment-reference "0000000FAKTNR153",
  :amount "000000100000", :payer-id "0000000000000111", :payment-date "20091110"}
 {:id "credit", :status "1", :payment-reference "0000000FAKTNR151",
  :amount "000000100000", :payer-id "0000000033331022", :payment-date "20091110"})

{% endhighlight %}

### Not just strings, real data types

Finally we add parsing of correct data types. We use the tag
`:data-type` we included in the rule book. We let a
[multimethod](http://clojure.org/multimethods) dispatch on the
`:data-type`. The default is just to return the string. As input to
the multimethod we give it the segment defintion, together with the
value to be parsed as `:value`. Below are a couple of different data
type implementation, for dates and amounts and so on.

{% highlight clojure %}
(defn date-formatter [format timezone]
  (let [d (java.text.SimpleDateFormat. format)]
    (.setTimeZone d (java.util.TimeZone/getTimeZone timezone))
    d))

(defmulti data-type :data-type)
(defmethod data-type :date [s]
  (.parse (date-formatter "yyyyMMdd" "Sweden") (:value s)))
(defmethod data-type :datetime [s]
  (.parse (date-formatter "yyyyMMddHHmmss" "Sweden") (:value s)))
(defmethod data-type :long [s] (Long/parseLong (:value s)))
(defmethod data-type :amount [s]
  (let [v (:value s)]
    {:kr (Long/parseLong (subs v 1 10))
     :ore (Long/parseLong (subs v 10))}))
(defmethod data-type :default [s] (:value s))
{% endhighlight %}

To use the data parsing we extend out definition of extract-str to
call it before returning.

{% highlight clojure %}
(defn extract-str [s segment]
  (let [start (:start-pos segment)
        end (:end-pos segment)
        s (subs s (dec start) end)]
    (data-type (assoc segment :value s))))

{% endhighlight %}

Running the same example again, we get a much nicer data set: 

{% highlight clojure %}
(parse-file "data/dd.txt" (load-rulebook "rules/dd.clj"))

({:id "opening-record", :account 9912346, :customer-number 471117,
  :datetime-written #inst "2009-11-10T19:30:55.000-00:00"}
 {:id "debit", :status 0, :payment-reference "000000RIDLEKTION",:amount {:kr 3000, :ore 0},
  :payer-id "0000000000000101", :payment-date #inst "2009-11-09T23:00:00.000-00:00"}
 {:id "debit", :status 0, :payment-reference "0000000FAKTNR156", :amount {:kr 3000, :ore 0},
  :payer-id "0000000000000102", :payment-date #inst "2009-11-09T23:00:00.000-00:00"}
 {:id "debit", :status 0, :payment-reference "0000000FAKTNR157", :amount {:kr 3000, :ore 0},
  :payer-id "0000000000000103", :payment-date #inst "2009-11-09T23:00:00.000-00:00"}
 {:id "credit", :status 0, :payment-reference "0000000FAKTNR153", :amount {:kr 1000, :ore 0},
  :payer-id "0000000000000111", :payment-date #inst "2009-11-09T23:00:00.000-00:00"}
 {:id "credit", :status 1, :payment-reference "0000000FAKTNR151", :amount {:kr 1000, :ore 0},
  :payer-id "0000000033331022", :payment-date #inst "2009-11-09T23:00:00.000-00:00"})
{% endhighlight %}

### Generate flat files 
Another cool thing with this approach is that it is
equally simple to use the same rulebook to generate flatfiles given
the data structure. Instead of parsing the rows, we create
formatters to generate fixed width output.

### Similar articles

- [Querying a CSV set like a database, using Datalog]({% post_url 2014-02-12-datalog-querying-csv-data %})

If you liked this article, let me know! Send me an [email](mailto:fredrik.dyrkell@gmail.com) or follow me on Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).


