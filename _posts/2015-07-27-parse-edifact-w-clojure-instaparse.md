---
layout: post
title: Parsing EDIFACT with Clojure's Instaparse
published: true

---

## The structure of EDIFACT files

[EDIFACT](https://en.wikipedia.org/wiki/EDIFACT) is a standardized
text-based format that enables companies to send business messages
between each other ([EDI](https://en.wikipedia.org/wiki/Electronic_data_interchange)).


### EDIFACT ORDERS example
Here's a small example, to give you an idea of what EDIFACT look like.

{% highlight text %}
UNB+UNOC:3+SE1212121212:ZZZ+DE3434343434:ZZZ+150728:0000+1234567'
UNH+1+ORDERS:D:96A:UN'
BGM+220+100'
DTM+4:20150701:102'
NAD+BY+++Buyer company+Street name+City'
LIN+1++Article #4232:SA'
QTY+47:40'
UNS+S'
CNT+2:1'
UNT+9+1'
UNZ+1+1234567'
{% endhighlight %}

This entire thing is called a **message**. On the second line, you can
read the message type: ``ORDERS``, a
[purchase order message](http://www.unece.org/trade/untdid/d96a/trmd/orders_d.htm).

Each line is called a **segment**. The line-breaks are optional, but
convenient for displaying and reading.

A segment consists of

- a **tag**, the first three characters, usually letters but can be alpha numerical.
- one or more **elements**. Each element is separated by a delimiter.
  In our case the delimiter is the symbol + (plus)
- An element can either be **simple**, i.e. it contains the value directly
  or it can be **composite**.
- A composite element consists of two or more values separated by
  another delimiter, namely : (colon).
- A segment terminator ' (single quote).

It is possible to define your own delimiters, using an ``UNA`` segment
in the beginning of the file. We will use the default delimiters here.

Let's break one of the segments into it's pieces.


{% highlight text %}
LIN+1++Article #4232:SA'
{% endhighlight %}

The tag of this segment is ``LIN``. It has three elements.

1. The number "1".
2. An empty element.
3. A composite element of two parts:
   1. "Article #4243"
   2. "SA"

To interpret what the meaning of the different elements are, we look
in the [EDIFACT specification](http://www.unece.org/trade/untdid/d96a/trsd/trsdlin.htm)
which tells us that this segment is a **line item** and the item number is 1.
The third element is the **item number identification**. "SA" is the
[item number code](http://www.unece.org/trade/untdid/d96a/uncl/uncl7143.htm)
which stands for **supplier's article number**, which in our case was
"Article #4243".


## Parsing in Clojure: Instaparse

In the Clojure world, there exists this very nice parser library
called [Instaparse](https://github.com/Engelberg/instaparse). It aims
to let you describe your grammar using standard [EBNF notation](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_Form), and turn it into an executable parser.

Step by step, let us turn our informal description of EDIFACT
segments into simple EBNF notation.

## EBNF grammar

A message consist of one or more segments.
{% highlight text %}
  message ::= segment+
{% endhighlight %}

A segment is a tag, followed by one or more elements, ending with a
terminator and optionally a new line.
{% highlight text %}
  segment ::= tag element+ terminator newline?
{% endhighlight %}

Finally, an element is just a element delimiter followed by an element
component. In turn, a component is either simple, or composite, and a
composite component is two or more simple values separated by the
component delimiter.

{% highlight text %}
element        ::= elem-delim elem-component
elem-component ::= simple | composite
composite      ::= simple (component-delim simple)*
simple         ::= chars
{% endhighlight %}

There we have it. In fact, this is very close to how the parser is
described. The only addition I have made is to let ``chars`` be either
escaped chars or ordinary chars to account for escaping (using the
symbol ? (question mark)). E.g. if a text field contains a colon, it
should be preceded by a question mark (?:).

## Clojure version of the EBNF grammar

Let's have a look at the definition for our parser in Clojure.

{% highlight clojure %}
;; You need to require instaparse.core as insta, see Quickstart in
;; the Instaparse documentation (https://github.com/Engelberg/instaparse#quickstart)
(def parser (insta/parser
             "message = segment+
              segment = tag element+ terminator newline?
              tag = #'[A-Z0-9]{3}'
              element = elem-delim elem-component
              <elem-component> = simple | composite

              <composite> = simple (component-delim simple)*
              <simple> = chars

              chars = (escaped-char | char)*
              escaped-char = #'\\?.'
              <char> = #'[^+:\\'\\?]+'

              <elem-delim> = <'+'>
              <component-delim> = <':'>
              <newline> = <'\\r'?> <'\\n'>
              <terminator> = <\"'\">"))
{% endhighlight %}

The angle brackets on the left side is used for [hiding tags](https://github.com/Engelberg/instaparse#hiding-tags) in the resulting tree, and angle brackets on the right hand side is for
[hiding values](https://github.com/Engelberg/instaparse#hiding-content). For example, the delimiters are hidden entirely.


In order to preserve the element components correctly in the presence
of escaped characters, the tags for ``chars``  and ``escaped-char`` are
left in the parse tree.

The can be collapsed neatly using [``insta/transform``](https://github.com/Engelberg/instaparse#transforming-the-tree).

{% highlight clojure %}
(defn run-parser
  [s]
  (->> s
       parser
       (insta/transform
        {:chars str
         :escaped-char second})))
{% endhighlight %}

Let's have a look at a couple of examples.

{% highlight clojure %}
(run-parser "PAI+::42'")
;; =>
[:message [:segment [:tag "PAI"] [:element "" "" "42"]]]

(run-parser "FTX+REG+++Information?::about:regulatory:authority:'")
;; =>
[:message [:segment [:tag "FTX"] [:element "REG"] [:element ""] [:element ""] [:element "Information:" "about" "regulatory" "authority" ""]]]

(run-parser
 "UNB+UNOC:3+SE1212121212:ZZZ+DE3434343434:ZZZ+150728:0000+1234567'
UNH+1+ORDERS:D:96A:UN'
BGM+220+100'
DTM+4:20150701:102'
NAD+BY+++Buyer company+Street name+City'
LIN+1++Article #4232:SA'
QTY+47:40'
UNS+S'
CNT+2:1'
UNT+9+1'
UNZ+1+1234567'")
;; =>
[:message
 [:segment [:tag "UNB"] [:element "UNOC" "3"]
  [:element "SE1212121212" "ZZZ"] [:element "DE3434343434" "ZZZ"]
  [:element "150728" "0000"] [:element "1234567"]]
 [:segment [:tag "UNH"] [:element "1"] [:element "ORDERS" "D" "96A" "UN"]]
 [:segment [:tag "BGM"] [:element "220"] [:element "100"]]
 [:segment [:tag "DTM"] [:element "4" "20150701" "102"]]
 [:segment [:tag "NAD"] [:element "BY"] [:element ""] [:element ""] [:element "Buyer company"] [:element "Street name"] [:element "City"]]
 [:segment [:tag "LIN"] [:element "1"] [:element ""] [:element "Article #4232" "SA"]]
 [:segment [:tag "QTY"] [:element "47" "40"]]
 [:segment [:tag "UNS"] [:element "S"]]
 [:segment [:tag "CNT"] [:element "2" "1"]]
 [:segment [:tag "UNT"] [:element "9"] [:element "1"]]
 [:segment [:tag "UNZ"] [:element "1"] [:element "1234567"]]]


{% endhighlight %}


If you have any comments or feedback, don't hesitate to send me an
[email](mailto:fredrik.dyrkell@gmail.com) or a message on Twitter
[@lexicallyscoped](https://twitter.com/lexicallyscoped).
