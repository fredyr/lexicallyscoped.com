---
layout: post
title: Designing large systems

---

We're moving away from simple systems and monolithic frameworks and building larger systems composed of multiple processes and services. This introduces new considerations in our systems designs, such as new failure modes and designing for resilience.

Here are 3 really good resources I've found valuable in this area.

### Resources

1. [Rich Hickey on The Language of the System](http://skillsmatter.com/podcast/scala/the-language-of-the-system) -- Rich talks about how interfaces, protocols and the semantics of components implicitly creates a "language of the system"

2. [Release it! Design and Deploy Production-Ready Software](http://pragprog.com/book/mnee/release-it) -- This book really underlines why I think Devops is an essential part of large scale distributed software

3. [Making reliable distributed systems in the presence of software errors](http://www.erlang.org/download/armstrong_thesis_2003.pdf) -- Fault tolerance and isolation by assuming that anything can fail.
