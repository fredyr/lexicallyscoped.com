---
layout: post
title: Transients in Clojure

---

Yesterday I spent an hour in the morning reading through some of the Clojure code in the [Graph library](https://github.com/Prismatic/plumbing) by [Prismatic](http://getprismatic.com). I do recommend having a look at [Jason Wolfes presentation about Graph](http://www.infoq.com/presentations/Graph-Clojure-Prismatic), it is very interesting. The code itself is very readable, although the nitty-gritty of the graph manipulations would require more work to understand fully.

The thing I wanted to focus on here, was one of the utitily functions I stumbled on that forms a basic building block for many of the higher level operations on graphs, namely the ``for-map``.   

The ``for-map`` is basically a for comprehension but for creating maps instead of lists. In Clojure you can use for comprehensions like this:

{% highlight clojure %}
(for [i (range 2)
      j (range 3)]
  [i j (even? (+ i j))])
;; ([0 0 true] [0 1 false] [0 2 true] [1 0 false] [1 1 true] [1 2 false])
{% endhighlight %}

Similarly you can create a map using ``for-map`` with:

{% highlight clojure %}
(for-map [i (range 2)
          j (range 3)]
         [i j] (even? (+ i j)))
;; {[0 0] true, [0 1] false, [0 2] true, [1 0] false, [1 1] true, [1 2] false}
{% endhighlight %}

Remember that in 
[Clojure maps](http://clojure.org/data_structures#Data%20Structures-Maps%20%28IPersistentMap%29), your keys can be much more than strings or keywords: anything that supports hashCode and equals can be a key. In this example we have a list with two integers as keys.

Now, we can easily implement this functionality using for comprehensions to create the values and Clojures polymorphic sequence functions:

{% highlight clojure %}
(into {}
      (for [i (range 2)
            j (range 3)]
        [[i j] (even? (+ i j))]))
;; {[0 0] true, [0 1] false, [0 2] true, [1 0] false, [1 1] true, [1 2] false}
{% endhighlight %}

And turning it into a macro for generic use:

{% highlight clojure %}
(defmacro for-map
  [seqs keys vals]
  `(into {}
         (for [~@seqs]
             [~keys ~vals])))
{% endhighlight %}

So, let's look at the actual definition of ``for-map``, from [``plumbing/core.clj``](https://github.com/Prismatic/plumbing/blob/master/src/plumbing/core.clj):

{% highlight clojure %}
(defmacro for-map
 ([seq-exprs key-expr val-expr]
    `(for-map ~(gensym "m") ~seq-exprs ~key-expr ~val-expr))
 ([m-sym seq-exprs key-expr val-expr]
    `(let [m-atom# (atom (transient {}))]
       (doseq ~seq-exprs
         (let [~m-sym @m-atom#]
           (reset! m-atom# (assoc! ~m-sym ~key-expr ~val-expr))))
       (persistent! @m-atom#))))
{% endhighlight %}

Clearly there's something else going on here, so let's dig into that a bit. For simplicity we can ignore the optional symbol (It gives a way to reference the partial collection from the keys and values). The code then becomes:

{% highlight clojure %}
(defmacro for-map
  [seq-exprs key-expr val-expr]
  `(let [m-atom# (atom (transient {}))]
     (doseq ~seq-exprs
       (reset! m-atom# (assoc! @m-atom# ~key-expr ~val-expr)))
     (persistent! @m-atom#)))
{% endhighlight %}

The reason for having this complex implementation is performance. Our naive implementation first creates an immutable list and iterates through the list to create a map. 

The code uses something called [transients](http://clojure.org/transients) to achieve this performance gain. Rich Hickey is explaining transients in the previous link much better than I can, but the point of transients, is to allow **local** mutability. The input and output of the ``for-map`` are still immutable data - but internally in the function, the structure is created using mutations. 

It is done, as we can see in the code, in three steps.
1. We obtain a mutable reference of the collection using the ``transient`` function
2. Mutations as being performed on the transient collection (using ``assoc!``).
3. An immutable reference of collection is returned as the result by calling ``persistent!``.

The important point here is that the reference to the mutable collection never leaves the function, but is purely local. 




