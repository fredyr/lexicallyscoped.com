---
layout: post
title: Porting my binary clock to Elm

---

### Binary clock in Clojurescript/Om ###

About a year ago I was playing with
[Clojurescript](http://clojure.org/clojurescript) and
[Om](https://github.com/swannodette/om), and made a small binary clock
with it. You can read the original blog post
[here](/2014/01/23/clojurescript-react-om-binary-clock.html).

A couple of ports were created, in [Reagent](http://holmsand.github.io/reagent/), and in [Hoplon](http://hoplon.io/). Check
them out!

- [Reagent port](http://holmsand.github.io/reagent/news/binary-clock.html)
- [Hoplon port](http://pmbauer.github.io/2014/01/27/hoplon-binary-clock/)

Porting the same application to different languages or
libraries/frameworks is a neat idea: it gives you a way to reason about
different solutions of a problem, together with their inherent
advantages and disadvantages. The most famous app in this category is
perhaps [TodoMVC](http://todomvc.com/). 

### Elm ###

[Elm](http://elm-lang.org/) is a
[functional programming](http://en.wikipedia.org/wiki/Functional_programming)
languange, related to
[Haskell](https://www.haskell.org/haskellwiki/Haskell). It compiles
down to Javascript and is intended for interactive applications.
Specifically it builds heavily on the idea of [Functional Reactive Programming](http://elm-lang.org/learn/What-is-FRP.elm).

Surely it would be fun to port the binary clock to Elm!

### Some Elm resources ###

I found the following links helpful.
 
- [Elm TodoMVC example](https://github.com/evancz/elm-todomvc/)
- [elm-html](http://package.elm-lang.org/packages/evancz/elm-html/1.0.0/)
- [Elm syntax](http://elm-lang.org/learn/Syntax.elm)
- [Elm Standard Libraries](http://package.elm-lang.org/packages/elm-lang/core/1.0.0/)

### Walkthrough ###

Firstly, the final result can be watched [here](/demo/elm-binclock/),
and the complete code is found on [Github]().

{% highlight haskell %}
module BinClock where

import Graphics.Element (Element, container, midTop)
import Html (..)
import Html.Attributes (..)
import Signal
import Window
import List
import Bitwise
import Time (..)
import Date 
{% endhighlight %}

The clock is made of cells. We have two kinds, the clock and the
legend. The clock cells, `cellCol`, are empty, but have two different colors, if
the bit is lit or not. The legend cells, `cellVal`, doesn't have a background
color, but instead contains a digit.

{% highlight haskell %}
cellCol : Bool -> Html
cellCol bit =
    let color = if bit then "light" else "dark"
    in div [class ("cell" ++ " " ++ color)] []
    
cellVal : Int -> Html
cellVal digit = div [class "cell"] [text (toString digit)]
{% endhighlight %}

I kept the data representation pretty close to the Clojurescript
original: a `BitNum` is a pair containing the digit it represents, and
a list of `Bool` corresponding to the bit representation of the digit. 

In turn, a `column` takes a `BitNum` and creates a list of cells for
the bit representation, wrapped up in html markup.

{% highlight haskell %}
type alias BitNum = (Int, List Bool)

column : BitNum -> Html
column (digit, bits) =
    let cells = (List.map cellCol bits) ++ [cellVal digit]
    in div [class "col"] cells

columns : List BitNum -> Html
columns cs =
    let cols = List.map column cs
    in div [class "colpair"] cols

legend : List Int -> Html
legend digits =
    let cells = List.map cellVal digits
    in div [class "col legend"] cells
{% endhighlight %}

We also need some code to take numbers, get the decimal parts, and
create `BitNum`'s out of them:

{% highlight haskell %}
decimalParts : Int -> List Int
decimalParts n = [n // 10, rem n 10]

toBitNum : Int -> BitNum
toBitNum n =
    let masks = List.map2 Bitwise.and [8, 4, 2, 1] (List.repeat 4 n)
        setp  = \x -> x > 0
        bits  = List.map setp masks
    in (n, bits)
{% endhighlight %}

The main view conclude the markup part were we crank everything
together. It takes current `Time` as input and uses all of our markup
parts to build the clock.

{% highlight haskell %}
view : Time -> Html
view t =
    let conv = \x -> x |> decimalParts |> (List.map toBitNum)
        d = Date.fromTime t
        cols = [Date.hour d, Date.minute d, Date.second d]
               |> List.map conv
               |> List.map columns
    in div [] ([legend [8,4,2,1]] ++ cols)
{% endhighlight %}

I mostly borrowed the startup code from the TodoMVC example. Note that
the main signal is augmented with `Time`, triggered every second.

{% highlight haskell %}
main : Signal Element
main = Signal.map2 scene (every second) Window.dimensions

scene : Time -> (Int,Int) -> Element
scene t (w,h) =
    container w h midTop (toElement w h (view t))
{% endhighlight %}

That's all, I hope you liked it!

### Ports in other languages?
Wouldn't it be cool to have ports in
[Purescript](http://www.purescript.org/) or
[GHCJS](https://github.com/ghcjs/ghcjs)? Or maybe
[Idris](http://www.idris-lang.org/) or
[Funscript](http://funscript.info/) for that matter? Maybe I will. Or
maybe you will? Let me know in any case.


If you have any comments or feedback,
send me an [email](mailto:fredrik.dyrkell@gmail.com) or send me a message on
Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).


