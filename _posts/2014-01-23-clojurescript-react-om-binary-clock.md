---
layout: post
title: Binary clock with Om, Clojurescript and React

---

### Binary clock
I've continued to play around with [Om](https://github.com/swannodette/om) as it has evolved over the last few weeks. 

I thought I'd share a little piece I made -- a simple binary clock. If you haven't encountered them before, the [wikipedia page](http://en.wikipedia.org/wiki/Binary_clock) gives a good description. The variant I have implemented is where hours, minutes and seconds each is represented by two columns: one for each digit. Each column in turn has four bits.

You can find the entire code on [github](https://github.com/fredyr/binclock/blob/master/src/binclock/core.cljs), and an online demo  [here](/demo/binclock/).  

### Application logic

The application logic is pretty straight forward. We take the current time and parse it out into a suitable bit representation.

{% highlight clojure %}
(defn get-time
  "current time as a map"
  []
  (let [d (js/Date.)]
    {:hours (.getHours d)
     :minutes (.getMinutes d)
     :seconds (.getSeconds d)}))

(defn decimal-parts
  "split a 1 or 2 digit number into its decimal parts
   e.g. 53 => [5 3], 9 => [0 9]"
  [n]
  [(quot n 10) (mod n 10)])

(defn bit-match 
  "bit-test over a list of bit indices"
  [n bits]
  (mapv (partial bit-test n) bits))

(defn n->bits
  "number => number + bit lists 
   e.g 53 => [[5 [false true false true]] [3 [false false true true]]]
   we're keeping the original digit so that we can show them together with
   the bit patterns later on"
  [n]
  (mapv #(vector % (bit-match % [3 2 1 0])) (decimal-parts n)))

(defn time->bits
  "converts time (in the format from get-time) to bit vectors"
  [time]
  (let [->bits (fn [coll key]
                 (update-in coll [key] n->bits))]
    (-> time 
        (->bits :hours)
        (->bits :minutes)
        (->bits :seconds))))
{% endhighlight %}

The applications state is stored in an atom.

{% highlight clojure %}
(def app-state (atom {:time (time->bits (get-time))
                      :legend [8 4 2 1]}))
{% endhighlight %}

Since we're going to use both boolean values and integers as cursors, we have to implement the clonable interface for those. The booleans are for our bit representation, and the numbers for the legend. I've also added the legend digits to the application state.

{% highlight clojure %}
(extend-type boolean
  ICloneable
  (-clone [b] (js/Boolean. b)))

(extend-type number
  ICloneable
  (-clone [n] (js/Number. n)))

{% endhighlight %}

### Om/React components

So here comes the presentation logic. A cell is div representing a single bit. If the bit is "one" (a.k.a true) we give it a light color, otherwise dark. From there we build a column and pairs of columns.

{% highlight clojure %}

(defn cell
  "react component for one single cell, input state is all bits for this
  column with options map containing index."
  [bit owner]
  (let [color (if (om/value bit) "light" "dark")]
    (om/component (dom/div #js {:className (str "cell" " " color)} nil))))

(defn column
  "react component containing one column of the clock"
  [[digit bits] owner]
  (om/component
   (dom/div #js {:className "col"}
            (om/build-all cell bits)
            (dom/div #js {:className "cell"} (om/value digit)))))

(defn column-pair
  "react component of two digits columns, such as hour or minutes or seconds"
  [[msd lsd] owner]
  (om/component
   (dom/div #js {:className "colpair"}
            (om/build column msd)
            (om/build column lsd))))
{% endhighlight %}

The legend is even simpler. We have to use `om/value` in each of these cases to get the actual values from the cursor wrapped around our booleans and numbers.

{% highlight clojure %}
(defn legend-cell
  "show one digit value in the legend"
  [digit owner]
  (om/component (dom/div #js {:className "cell"} (om/value digit))))

(defn legend-column
  "column showing the digit value of each row"
  [digits owner]
  (om/component
   (dom/div #js {:className "col legend"}
            (om/build-all legend-cell digits))))
{% endhighlight %}

Finally we kick-start the rendering loop with an `om/root`. You can find out more about the lifecycle protocols in the [Om documentation](https://github.com/swannodette/om/wiki/Documentation), as well as the [React component and lifecycle spec](http://facebook.github.io/react/docs/component-specs.html). In the `will-mount` we setup a timer callback to update our application state with the new time, which will trigger the component to (re-)render.

{% highlight clojure %}
(om/root
 app-state
 (fn [{:keys [legend time] :as app} owner]
   (reify
     om/IWillMount
     (will-mount [_]
       (js/setInterval
        (fn [] (om/update! time #(time->bits (get-time)))) 1000))
     om/IRender
     (render [_]
       (dom/div nil
                (om/build legend-column legend)
                (om/build column-pair (:hours time))
                (om/build column-pair (:minutes time))
                (om/build column-pair (:seconds time))))))
 (.getElementById js/document "content"))

{% endhighlight %}

If you liked this article, let me know! Send me an [email](mailto:fredrik.dyrkell@gmail.com) or follow me on Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).


