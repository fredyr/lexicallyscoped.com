---
layout: post
title: Functional programming building blocks

---

I've been really focusing on functional programming lately, and not necessarily in functional languages, but the underlying concepts and how to apply them in the languages I'm currently using. Here I've put together a small compilation of the most fundamental building blocks in functional programming together with links to resources about them.

### Functional programming concepts

John Hughes wrote a famous paper called [Why Functional Programming Matters](http://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf), in which he focuses on [higher-order functions](http://en.wikipedia.org/wiki/Higher-order_function) and [lazy evaluation](http://en.wikipedia.org/wiki/Lazy_evaluation). Higher-order functions helps you be more [declarative, writing what you want](http://en.wikipedia.org/wiki/Declarative_programming), not [how you compute it](http://en.wikipedia.org/wiki/Imperative_programming). [List comprehensions](http://learnyouahaskell.com/starting-out) is also useful for being declarative.

Having [functions as first class values](http://en.wikipedia.org/wiki/First-class_function) together with [lexical scope](http://en.wikipedia.org/wiki/Scope_(computer_science) gives you the power to [encapsulate data and behaviour](http://howtonode.org/why-use-closure) as an object in [OOP](http://en.wikipedia.org/wiki/Object-oriented_programming) just using functions.

By limiting [side effects](http://en.wikipedia.org/wiki/Side_effect_%28computer_science%29) and using [pure functions](http://en.wikipedia.org/wiki/Pure_function) makes it easier to reason about program behaviour since it avoids mutating states.

Functional programming promotes using [values](http://martinfowler.com/eaaCatalog/valueObject.html), that are [immutable](http://en.wikipedia.org/wiki/Immutable_object). Apart from the benefits immutability gives in concurrent programming, it also separates values from [state and identity](http://clojure.org/state).

### Taking the most important parts from OOP

Some languages try to incorporate the object oriented paradigm together with functional programming, most notably [Scala](http://www.scala-lang.org/). In Clojure you still get the benefits from [encapsulation and polymorphism](http://thinkrelevance.com/blog/2009/08/12/rifle-oriented-programming-with-clojure-2), while going as far as claiming [OOP to be overrated](http://clojure.org/rationale).

