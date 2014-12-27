---
layout: post
title: Clojure version of accumArray - A generalization of fold (reduce) for arrays

---

### Haskell?.. isn't that like, weird and stuff?

In [Haskell](http://www.haskell.org/haskellwiki/Haskell) there is a neat generalization of fold (or reduce as it's also called) for arrays. It's called [`accumArray`](http://hackage.haskell.org/package/array-0.3.0.2/docs/Data-Array.html), and lives in the `Data.Array` module. Here it is in action:

{% highlight haskell %}
import Data.Array

elems $ accumArray (+) 0 (1,3) [(1,2),(1,4),(2,1),(2,2),(2,3),(3,5)] 
-- [6,6,5]
{% endhighlight %}

Let's compare it to an ordinary reduction.

{% highlight haskell %}
foldr (+) 0 [2,4,6,8,10]
-- 30
{% endhighlight %}

Given a function, an initial value and a list of values, we incrementally accumulate the values in the list using the function, starting with the initial value.

Similarly `accumArray` takes a accumulator function and an initial value. But in addition, it also takes the bounds of an array, in this case `(1,3)`, in which all positions are initialized with the initial value.
Finally, instead of just a list of values, we have an association list, that is a list of pairs. In each pair the first element denotes an `index` in the array on which to perform the reduction, and the second element is the actual value. 

In a sense you can think of it as doing multiple reductions at once -- using the index to coordinate in which of the reduction each value goes. 


Well, Haskell is all cool, but we want this in [Clojure](http://clojure.org/) too, right?

![Clojure all the things](http://i.imgur.com/h1I7Uek.jpg)

### I don't usually mutate, but when I do, I do it locally

Because `accumBuffer` deals with fixed size arrays, my first thought for the implementation was to use plain Java arrays. 

{% highlight clojure %}
(defn accum-array
  [acc-fn init size assoc-list]
  (let [arr (make-array (type init) size)
        accum (fn [[index a]]
                (aset arr index (acc-fn (aget arr index) a)))]
    (java.util.Arrays/fill arr init)
    (dorun (map accum assoc-list))
    (into [] arr)))
{% endhighlight %}

The implementation is pretty straight forward. We map over each item in the association list and mutate the array in place. Instead of returning the array as is, we turn it into a persistent vector, so the mutations are only local to the function.

On the other hand, when doing local mutation, it is more idiomatic to use [Clojure transients](http://clojure.org/transients).

Using transients doesn't change the structure of the code much:

{% highlight clojure %}
(defn accum-array'
  [acc-fn init size assoc-list]
  (let [arr (transient (into [] (take size (repeat init))))
        accum (fn [[index a]]
                (assoc! arr index (acc-fn (nth arr index) a)))]
    (dorun (map accum assoc-list))
    (persistent! arr)))
{% endhighlight %}

Let's try some examples.

We can reduce over a list of `booleans` using `or`:
{% highlight clojure %}
;; or is a macro, so we need a function wrapper around it
(defn disjunct [a b] (or a b))
(accum-array'
 disjunct false 10
 [[0 true] [8 true ] [9 true]])
;; => [true false false false false false false false true true]
{% endhighlight %}

The major difference compared to the Haskell version is that we only specify the size of the array, not the lower and upper bound. The association list is represented as nested vectors. But due to Clojure's sequence abstraction we can use nested lists just as easily. The return type will always be a vector though.

With a [`zip`](http://hackage.haskell.org/package/base-4.6.0.1/docs/Data-List.html#g:17) function we can generate the association list a bit more easily:

{% highlight clojure %}
(def zip (partial map vector))
(accum-array'
 + 0 10
 (zip [0 1 4 1 3 6 3 9 3] (repeat 1)))
;; => [1 2 0 3 1 0 1 0 0 1]
{% endhighlight %}

### Finding the smallest (natural) number not in a list 

We can now put our new function to real use,  by computing the smallest number, zero or larger, that's not in a given (unsorted) list. 

This problem, with a really nice solution (in Haskell) is given in Richard Bird's book [Pearls of Functional Algorithm Design](http://www.amazon.com/Pearls-Functional-Algorithm-Design-Richard/dp/0521513383), that I have enjoyed browsing lately. I can highly recommend it for anyone interested in functional programming, regardsless of programming language preference.

In Clojure, the solution would look something like

{% highlight clojure %}
(defn checklist [xs]
  (let [n (count xs)]
    (accum-array' disjunct false (inc n)
                 (zip (filter (partial >= n) xs) (repeat true)))))

(def search (comp count (partial take-while identity)))
(def minfree (comp search checklist))

(minfree [0 1 2 3 5 6 2])
;; => 4
(minfree [8 23 9 0 12 11 1 10 13 7 4 14 5 17 3 19 2 6])
;; => 15
{% endhighlight %}


If you liked this article, let me know! Send me an [email](mailto:fredrik.dyrkell@gmail.com) or follow me on Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).
