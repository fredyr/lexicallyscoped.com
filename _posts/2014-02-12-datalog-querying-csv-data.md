---
layout: post
title: Querying CSV data with Datalog

---

### Querying CSV data

I've been wanting to try out Datomic's datalog for a while (not just for Datomic, but as a stand-alone query engine), but never got around to it. But some weeks ago I stumbled on two different links, that brought this idea back. 

### TextQL -- execute SQL against structured text like CSV

On [Hacker News](https://news.ycombinator.com/item?id=7175830) I found a command line tool [TextQL](https://github.com/dinedal/textql) to do SQL querying against text data. It works by importing the structured text into a sqlite database.

Of course, if simply filtering for some text string is enough, ``grep`` would probably work just fine, but for any type of relational query, such as join etc, you get that extra boost with a query engine.

### Using core.logic to query custom data sources

While browsing around the internet in search for interesting things in Clojure I found [Timothy Baldridge](https://github.com/halgari) ([@timbaldridge](https://twitter.com/timbaldridge)) YouTube video on using [Core.Logic With Custom Data Sources](http://www.youtube.com/watch?v=HHZ8iqswiCw). Here, core.logic is used to create relational queries over CSV data. [Code from the video](https://gist.github.com/halgari/7160778).

By the way, if you haven't seen his other YouTube videos on the [Core Async Go Macro Internals](http://www.youtube.com/watch?v=R3PZMIwXN_g) and [Let's Write a JIT](http://www.youtube.com/watch?v=Y8gttn9xmtA), you should definitely check those out! 

### Datomic

[Datomic](http://www.datomic.com/) is to the database world what [persistent collections](http://en.wikipedia.org/wiki/Persistent_data_structure) are to data structures, favoring immutability over in-place mutation. Datomic comes with a query engine which is based on [Datalog](http://en.wikipedia.org/wiki/Datalog). Perhaps surprising, is that the query engine isn't tied tighly to the database, but can be used against the ordinary data structures in Clojure.

### Trying a query

To start off, we add Datomic and a CSV parser to our project. 

{% highlight clojure %}
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [com.datomic/datomic-free "0.9.4470"]
                 [clojure-csv/clojure-csv "2.0.1"]
{% endhighlight %}

Now we're ready to start querying:

{% highlight clojure %}

(ns datalog-query.core
  (:use [datomic.api :only (db q) :as d])
  (:require [clojure-csv.core :as csv]))

(let [[header & body] (csv/parse-csv (slurp "dataset.csv"))
      csv-data (into [] (filter #(= (count %) (count header)) body))]
  (q
   '[:find ?first ?last ?comp
     :in [[?first ?last ?comp ?address ?city ?county ?state]]
     :where [(= ?state "CA")]]
   csv-data))

{% endhighlight %}

I'm filtering all the lines in the CSV data, to ensure that the rows all have the same number of columns. 

### Continue exploring!

That's all to get started. To explore datalog further, have a look at the examples in [this gist](https://gist.github.com/stuarthalloway/2645453), or read the [Datomic query](http://docs.datomic.com/query.html) documentation.

If you liked this article, let me know! Send me an [email](mailto:fredrik.dyrkell@gmail.com) or follow me on Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).


