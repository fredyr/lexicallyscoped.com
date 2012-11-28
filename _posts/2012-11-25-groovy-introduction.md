---
layout: post
title: An introduction to Groovy

---

### Groovy, the Way Java Should Be

Okay, so I'm going to kick off this blog with a write up of a [Groovy](http://groovy.codehaus.org/) introduction training session I did a while back. 

The title above isn't mine (although I wouldn't mind if it was). It's actually from the excellent book [Groovy Recipes: Greasing the wheels of Java](http://pragprog.com/book/sdgrvr/groovy-recipes) by Scott Davies. 

Groovy, if you don't already know, is a dynamic language who runs on the JVM. It was designed to:

#### Have good interopability with Java

Groovy is designed to be hosted on the JVM, sharing the JVM type system making interopability simpler. 
Groovy classes are Java classes. Groovy arrays are Java arrays, and so on. In fact, most Java code is also valid Groovy code. [Clojure](http://clojure.org/jvm_hosted) is another example of a language that's hosted on the JVM, in contrast to for example JRuby and Jython who are ports of these languages for the JVM.

#### Reducing language verbosity
By adding syntactic sugar for common idioms the code can both be much more concise but also more declarative. 
#### [Duck typing](http://en.wikipedia.org/wiki/Duck_typing)
Groovy makes Java's static type system optional. Since type checking is done at runtime instead of at compilation we can avoid the verbose type declarations in the code and also open doors for powerful polymorphism possibilities.


#### Add features that were missing in Java
And the good thing about Groovy is that you don't have to wait for the next Java version or what ever to benefit from all the good features like closures, built-in literals for lists, maps and more.


### [REPL](http://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) Goodness    

This tutorial is based heavily on code samples so that you will be able to follow and test most of the code samples in the Groovy Console (either in the standard [Groovy installation](http://groovy.codehaus.org/) or in the [Groovy Web Console](http://groovyconsole.appspot.com/)) as you read along. Poking around and testing new stuff hands on is after all a great way to learn.

Let's wait no further, and look at some basic Groovy constructs!

{% highlight groovy %}
// In Java
for(int i = 0; i < 3; i++) {
  System.out.println("ho ");
}
System.out.println("merry christmas");

// Succinct Groovy Goodness
3.times { print "ho " }
println "merry christmas"
// => "ho ho ho merry christmas"


(1..3).each { print "$it " }
// => 1 2 3

// The above is really
(1..3).each({ print "$it"})

// But parenthesis are optional
// and trailing ; are also (almost) optional
{% endhighlight %}

{% highlight groovy %}
// Optional return statements
// The last evaluated expression is returned

def getFullName() {
  return "${firstName} ${lastName}"
}
// or
def getFullName() {
  "${firstName} ${lastName}"
}

// Didn't work properly in < Groovy 1.6
{% endhighlight %}

{% highlight groovy %}
// Typing is optional
String getFilename(Document document) {
  if(document instanceof Invoice) {
    Invoice invoice = (Invoice)document
    "QUACK_${invoice.getInvoiceNumber()}_INVOICE.xml"
  }
}

// or
def getFilename(invoice) {
  "QUACK_${invoice.getInvoiceNumber()}_INVOICE.xml"
}
{% endhighlight %}


{% highlight groovy %}
// Safe navigation operator
str?.reverse()

// instead of
if(str != null) {
  str.reverse()
}
{% endhighlight %}

Truths in Groovy land

{% highlight groovy %}

//true

if(1) // any non-zero value is true
if(-1)
if(!null) // any non-null value is true
if("John") // any non-empty string is true

Map family = [dad:"John" , mom:"Jane" ]
if(family) // true since the map is populated

def list = [1]
if(list) // true since the array length is greater than 0


//false

if(0) // zero is false
if(null) // null is false
if("") // empty strings are false

Map family = [:]
if(family) // false since the map is empty

def list = []
if(list) // false since the array is zero length
{% endhighlight %}

Having these values for true/false significantly remove boilerplate testing in conditionals and improve clarity

{% highlight groovy %}
if(str) {
//if(str != null && str != "") {
  doStuff(str);
}

if(list) {
// if(list != null && !list.isEmpty())
  doStuff(list);  
}
{% endhighlight %}

[String interpolation](http://en.wikipedia.org/wiki/String_interpolation)

{% highlight groovy %}
// Strings and GStrings

value = "Palladium"
println "${value} is a chemical element."
// Must be between "" and not ''

println "Strings in 'strings'"
println 'Strings in "strings"'

// Multiline strings
def value = 
"""<invoice id="2">
  <invoiceNumber>923934032</invoiceNumber>
</invoice>
"""
{% endhighlight %}

### Closures

In Groovy, functions are first class objects, which means that you can treat them like any other value. Pass them as arguments, return function values from other functions etc.

We have already sneaked in some closures earlier in the ``each`` loops by the way.

{% highlight groovy %}
def hi = {println "Hi"}
hi()
// => Hi

// Compare this with the function definition
def hi() {println "Hi"}

// "it" is the default name for the closure
def helloer = {println "Hello Mr. ${it}"}
helloer("Lind")
// => Hello Mr. Lind

// although it's possible to name the param
def helloer = {name, age -> 
  println "Hello Mr. ${name}, ${age} years old."
}
helloer("Lind", 25)

{% endhighlight %}

{% highlight groovy %}
def sum(list) {
    def total = 0
    list.each {
        total += it
    }
    total
}
println sum((1..100))
// => 5050

def prod(list) {
    def total = 1
    list.each {
        total *= it
    }
    total
}
println prod((1..10))
// => 3628800
{% endhighlight %}

Have a look at the code above. Most of the code structure is identical. Wouldn't it be cool if we could leverage closures to make it more [DRY](http://en.wikipedia.org/wiki/Don't_repeat_yourself)?

{% highlight groovy %}
def apply(list, func) {list.each {func(it)}}

def total = 1
apply((1..10), { total *= it })
println total


total = 0
apply((1..100), { total += it })
println total
{% endhighlight %}

A common idiom in functional languages is to use closures for predicates to work with collections and to do transformations. This is possible in Groovy as well.

{% highlight groovy %}
//  Lists - basic operations

def list = [1,4,5,3,"hello"]
println list[0]
// => 1
println list[1]
// => 4
println list[-1]
// => hello
println list[-2]
// => 3

// Slice
println list[1..3]
// => [4, 5, 3]
println list[2..-1]
// => [5, 3, hello]

list.add(12)
println list
// => [1,4,5,3,"hello",12]
{% endhighlight %}

{% highlight groovy %}
// Lists - filtering and such

list = [1, 3, 45, 2, 54]

println list.sort()
// => [1, 2, 3, 45, 54]

println list.collect { it * 2 }
// => [2, 6, 90, 4, 108]

println list.find { it > 4 }
// => 45

println list.findAll {it > 4}
// => [45, 54]

// Built-in sum for collections
(1..100).sum()
// => 5050

def strings = ["Hello", "everybody", "working", "at", "Pagero"]
println strings.collect { it.size() }.sum()
// => 29

println strings.join(" ")
// => Hello everybody working at Pagero
{% endhighlight %}

{% highlight groovy %}
// Maps

def map = ["RH": "Rich Hickey", "JS": "James Strachan"]
println map["RH"]
println map.RH
// => Rich Hickey

map.each { 
    println "Initials ${it.key} stands for ${it.value}"
}
map.each { key, value ->
    println "Initials $key stands for $value"
}
// => Initials RH stands for Rich Hickey
// => Initials JS stands for James Strachan

{% endhighlight %}


{% highlight groovy %}
// Predicates

def map = ["RH": "Rich Hickey", "JS": "James Strachan"]

// Does anyones last name end with ey?
map.any { initals, name ->
    name =~ /^.*ey$/
}
// => true

// Does everybodys last name end with ey?
map.every { initals, name ->
    name =~ /.*ey$/
}
// => false

// Works on lists in the same way
[1, 2, 3].any { it % 2 == 0 }
// => true

{% endhighlight %}







