---
layout: post
title: A brief introduction to OCaml

---

## Introduction to [OCaml](http://ocaml.org/) ##

A couple of weeks ago I did an introductory presentation on [OCaml](http://ocaml.org/)
at our [local meetup groups](http://www.meetup.com/got-lambda/) [@GotLambda](https://twitter.com/GotLambda).
The material is in the form of one long interactive session, in a
style similar to [learnxinyminutes.com](http://learnxinyminutes.com/).

I have previously written an introduction to [Purescript](http://www.purescript.org/) in this
fashion, which you can find here: [Learn Purescript in Y minutes](/2014/08/31/learn-purescript-in-y-minutes.html).
My previous presentation at GotLambda, can be found here, it was on [Domain Specific
Languages in Haskell](/2015/01/14/haskell-edsl-for-sharc.html).

## References for learning OCaml

###  Course material
  - Cornell's "CS 3110 - Data Structures and Functional Programming"
    have very good lecture notes [available online](http://www.cs.cornell.edu/Courses/cs3110/2014sp/lecture_notes.php)
  - [OCaml for the Skeptical](http://www2.lib.uchicago.edu/keith/ocaml-class/home.html),
    with course material found [here](http://www2.lib.uchicago.edu/keith/ocaml-class/class-01.html).

### Books
  - [Real World OCaml](https://realworldocaml.org),
    by Yaron Minsky, Anil Madhavapeddy, Jason Hickey.
    Arguably the best and most up-to-date book on OCaml, as well as freely available online.
  - [Introduction to Objective Caml](http://files.metaprl.org/doc/ocaml-book.pdf),
    by Jason Hickey.
  - [Developing Applications With Objective Caml](http://caml.inria.fr/pub/docs/oreilly-book/html/index.html),
    by Emmanuel CHAILLOUX, Pascal MANOURY, Bruno PAGANO.
  - [Using, Understanding, and Unraveling The OCaml Language](http://caml.inria.fr/pub/docs/u3-ocaml/),
    by Didier Remy


  > Tip: Focus on the material in Real World OCaml, and use the other
    resources as complementary material when you want more examples or
    alternative explanations of a concept.

### Articles
  - [Unreliable Guide to OCaml Modules](http://lambdafoo.com/blog/2015/05/15/unreliable-guide-to-ocaml-modules/)

###  Documentation
  The OCaml [website](http://ocaml.org/) has got a lot of good material.
  Most notably:

  - The [Manual](http://caml.inria.fr/pub/docs/manual-ocaml/) with standard library documentation
  - [Opam packages documentation](https://opam.ocaml.org/packages/)


If you have any comments or feedback, don't hesitate to
send me an [email](mailto:fredrik.dyrkell@gmail.com) or a message on
Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).
{% highlight ocaml %}
(*

INTRODUCTION TO OCAML


Fredrik Dyrkell
@lexicallyscoped

www.lexicallyscoped.com

*)

(*

  Short note on installing OCaml

  Follow the instructions for
  - `Real World OCaml` (https://realworldocaml.org/)
  - https://github.com/realworldocaml/book/wiki/Installation-Instructions
  which covers (among others)
  - Opam - the package manager
  - Utop - a modern interactive toplevel
  - Set up your environment
    #use "topfind";;

*)

(* Show all packages installed *)
#list;;

(*
  In Utop, as well as in the standard OCaml toplevel, every
  expressions needs to end with ;;

  Also, notice that # is used to mark a toplevel directive, not a comment.
*)

(* Load a package *)
#require "num";;
Num.num_of_int 42;;

(*
  TYPES

  The base types of OCaml are
  int, float, char, string/bytes, bool and unit

  (-safe-string introduced in OCaml 4.02 separates
  bytes from strings and make strings immutable)
*)

1;;
3.14;;
'c';;
"chars";;
true;; false;;
();;
(*
  The unit type, only has the one value (), commonly used as the
  value of a procedure that computes by side-effect. You can think of
  it as `void` in C/Java
*)

(* Aritmetic operations *)
12 + 44;;
sqrt 5.0;;
355 / 113;
355.0 / 113.0;;
9.2 *. 3.3;;

(* Boolean operations *)
1 = 1;; (* Structural equality *)
1 <> 2;;

1 == 1;; (* "Identical", physical equality (same pointer in memory) *)
1 != 2;;
(* Matters when you dig into mutable things *)

(* Similarly, less-than, greater-than, and, or *)
1 < 3 || 4 <= 2;;
1 >= 3 && 4 <= 2 || not true;;

(* String manipulations *)
"Hello" ^ " " ^ "world";; (* Concatenation *)
"Hello".[0];; (* Random access *)

(*
  Function application
  No parenthesis around or commas between arguments needed
 *)
String.sub "Hello" 1 2;; (* Substring *)
(*
  The function sub is in the String module -- we'll talk about
  modules later; for now, think of them as namespaces
*)
int_of_float 3.0;; (* No need for parenthesis *)
float_of_int 4;;

float_of_int 5 + 4;; (* Unless, well, you need them *)
(*
  This _of_ form is quite common.
  I usually read it out by adding `make` in front

  ``Make an int of float``
*)

(*
  If you want to know more about which operations are provided over
  the built-in types, have a look at the Pervasives module

  http://caml.inria.fr/pub/docs/manual-ocaml/libref/Pervasives.html

  We won't cover much more string operations in this introduction.
  Have a look at the String module for more

  http://caml.inria.fr/pub/docs/manual-ocaml/libref/String.html
 *)

(*
  Let-bindings - naming values and expressions

  Two different let variants:
  - local definitions
  - global definitions
*)

(* Local let definitions bind a value to a name in an expression *)
let x' = 3 in x' * 8

(*
  Variable names must start with a lowercase letter or underscore

  x' isn't bound to a value after this expression is evaluated, it is
  only locally bound

  As long as were writing complete definitions and not just
  expresssions to evaluate, we can omit the trailing semicolons and
  evaluate expressions directly
*)
let _ = int_of_float 3.14

(* We can nest the let expressions *)
let x = 4 in
let y = 3 * 4 in
4 - y - x * 2

(* Local let bindings are themselves expressions *)
let _ = 10 + (let n = 2 in n * n)


(*
  Global let definitions

  Instead of just creating local bindings, we can as easily create
  global (or toplevel) bindings
*)
let x = 3
let y = int_of_float 3.16
(* And mix global and local bindings *)
let z = let x = 2 in 3 * x

(*
  The global let bindings are just syntactic sugar for a `context`
  that's kept and all new definitions are evaluated in
*)
let a = 12;;
let b = 5;;
let c = a + 2 * b;;
c;;
(* Is actually equivalent to *)
let a = 12 in
    let b = 5 in
    let c = a + 2 * b in
    c

(* So when your using the same variable again, you're really just
	shadowing the previous definition, in the global context *)
let a = 12 in
    let a = 4 in
    a

(*
  Recursive definitions

  Since all let bindings really are just local definitions shadowing
  each other, we need to explicitly say we want to refer to a name
  recursively: let rec
 *)
let rec fac n =
  if n == 0 then 1 else n * fac (n - 1)

(* We incidentally introduced conditions above using if expressions *)
let abs x = if x > 0 then x else -x
(*
  Since everything is an expression in OCaml, you have to provide
  and else clause
*)


(*
  We haven't yet looked at how to

  Create functions
*)
(* Anonymous functions (lambda) *)
fun x -> x * x;;

(* Just assign it a global name *)
let sqr = fun x -> x * x

(*
  This is ofcourse so common that there is syntax for it

  - Adding the arguments after the name and
  - not having to specifying the `fun` keyword
 *)
let sqr x = x * x
let mul x y = x * y

(*
  All functions in OCaml take and return exactly one argument!

  But, how do you make functions with more arguments?
  Two choices:
  - Use tuples to package arguments into `one`
  - Currying

  The latter is default in OCaml. Lets look at an example
*)
let mult x y = x * y
(*
  The type signature for this function becomes
  val mult : int -> int -> int = <fun>

  Which really means:
  int -> (int -> int), i.e a function that takes an integer and
  returns a (one) new function.
  That function in turn, takes one int, and returns an int

  We can write it out like so
 *)
let mult = fun y -> (fun x -> x * y)

(*
  Okay, let's take a little step back now!

  (From `Introduction to Objective Caml` by Jason Hickey)


  OCaml is FUNCTIONAL -

  meaning that functions are treated as first-class values. Functions
  may be nested, functions may be passed as arguments to other
  functions, and functions can be stored in data structures. Functions
  are treated like their mathematical counterparts as much as
  possible.

 *)

(* Functions are first class *)
let inc = fun x -> x + 1
let dec = fun x -> x - 1
(* Let's define a function that takes a function as argument *)
let appl2 f x = f (f x)

let _ = appl2 inc 3
let _ = appl2 dec 3

(*
  We have already seen examples of returning functions in the currying
  examples
*)


(*

  OCaml is STRONGLY TYPED -

  meaning that the type of every variable and every expression in a
  program is determined at compile-time. Programs that pass the type
  checker are safe

  - No automatic coercion of types, explicit conversion
  - Not even same operators for int/float

*)

(*

  OCaml uses TYPE INFERENCE -

  to infer types for the expressions in a program. Even though the
  language is strongly typed, it is rare that the programmer has to
  annotate a program with type constraints.

  OCaml's type system is POLYMORPHIC, meaning that it is possible to
  write programs that work for values of any type.

  - We've already seen the inferencer in action
 *)

(* We can specify types if we want *)
let mult (x : int) (y : int) : int = x * y


(*
  Parametric polymorpism

  List.length;;
  has the type 'a list -> int = <fun>

  'a - a with a leading single quote is called a type variable

  For something like a list, we want to abstract over the type of
  elements stored in the list, so we can use them for ints, floats and
  so on. This is done by parameterizing the type with a type variable
*)
let listify x = [x]
(* OCaml automatically infers the most general type! *)

(*
  Tuples
  - int * string, int * int * float
  - Can be heterogeneous
  - Parenthesis are optional
 *)
let _ = 1, "five"
let _ = (1, 4, 5.0)


(*
  Lists
  - int list, string list
  - Immutable
  - Homogeneous (all elements must have the same type)
 *)
let xs = [1; 3; 23; 5; 77]
(*
  In a list, the elements are separated by semicolon
  The result in the example below may be surprising
 *)
let _ = [1, 2, 3]

let _ = 132 :: xs (* Prepend elem onto a list "cons" *)
let _ = [13; 54; 59] @ xs
let _ = List.length xs
(* Not recommended, since they break down on empty lists *)
let _ = List.hd xs
let _ = List.tl xs
let _ = List.hd [] (* Throws exception *)
let rec sevens = 7 :: sevens;;


(*
  Pattern matching

  Consists of two parts
  - Destructuring binding and
  - Matching (Akin to switch cases or if/elseif)


*)
let atuple = (1, "five")
(*
  Putting the tuple on the left, works as a destructuring bind
*)
let (x, y) = atuple
(* It works on functions too *)
let dot (x1, y1) (x2, y2) =
  x1 * x2 + y1 * y2
(* It does't just work on tuples of course *)
let alist = [1; 3; 4]
let (x :: xs) = alist

(*
  Note that the pattern matching isn't exhaustive
  This is because the code doesn't account for empty lists - cons
  assumes at least one element

  To cover more than one case, we have `match`
  where each pattern is described, separated by pipes |
 *)

let hd_or_else ys def = match ys with
  | []      -> def
  | x :: xs -> x

(*
  Let's see if we can build a function that reverses a list, shall we
*)
let rec rev_ack xs ys = match xs with
  | x :: xs' -> rev_ack xs' (x :: ys)
  | [] -> ys

let rev xs =
  let rec rev_ack xs ys = match xs with
    | x :: xs' -> rev_ack xs' (x :: ys)
    | [] -> ys
  in rev_ack xs []

let _ = rev [3;2;5;3;6]

(*
  Map and folds

  A lot of the time you can use the built in higher-order functions

*)

(* Map - Apply a function to all the elements in a list *)
let _ = List.map (fun x -> x * x) [9; 4; 3; 2]

(*
  Filter - create a new list wiht only the elements passing a
  predicate function
*)
let _ = List.filter (fun x -> x mod 2 = 0) [9; 4; 3; 2]

(* Reductions/Fold *)
let _ = List.fold_left (fun x y -> x + y) 0 [9; 4; 3; 2]
let _ = List.fold_left (+) 0 [9; 4; 3; 2]


(* Implement rev using fold instead *)
let rev_ack' xs = List.fold_left (fun ys' x' -> x' :: ys') [] xs

(*
  Data types (Sum types, Variant types)

  So far we've seen product types, such as tuples
  You can see the product in the type definition: int * float * int

  In OCaml we also have sum types, when you want either of two or more
  values, but not at the same time.

*)

type week_day = Mon | Tue | Wed | Thu | Fri
(*
  Alternatives are given with capital initial letter separated by
  pipes.

  Mon, Tue etc are called constructors. You can think of them as
  functions (in this case it doesn't take any arguments) and return a
  value of type week_day
 *)
let best_week_day = Fri


(* You can include types in your constructors *)
type num = Int of int | Float of float
(* Here, the "constructor function" `Int` has the type `int -> num`  *)

(*
  You've probably already guessed, but the way we use and extract
  values from our data types is by pattern matching

 *)

let num_to_float n = match n with
  | Int i -> float_of_int i
  | Float f -> f


let add x y = match (x, y) with
    | Float f, Float g -> f +. g
    | Int i,   Float g -> float_of_int i +. g
    | Float f, Int j   -> f +. float_of_int j
    | Int i,   Int j   -> float_of_int i +. float_of_int j

let _ = add (Float 5.4) (Int 3)


(* The bool datatype is not a magic built-in type *)
type bool = false | true

(*
  The Option type is already defined in OCaml
  It is especially useful in the cases where you sometimes don't have
  an answer for some computation
*)
type 'a option = None | Some of 'a

(* The head of a list is undefined for an empty list *)
let hd xs = match xs with
    []      -> None
  |  x :: _ -> Some x

let div x y =
  if y == 0 then None
  else Some (x / y)

(*
  Records

  - Unordered collection of *named* values
 *)

type book = {author : string; title : string; pages : int}
(*
  Note the colon in the type definition, but = for assigning values
  Separated by ; as for lists
 *)
let ps = {author="Peter F. Hamilton"; title="Pandoras Star"; pages=1144}
(* Records are immutable by default *)

(* Use dot notation to access data *)
let title b = b.title

(* Update syntax `with` -- creates a new record *)
let ju = {ps with title="Judas Unchained"; pages=1024}

(* Pattern matching (destructuring) allows to pluck values as args *)
let presentation {title; author} = title ^ " by " ^ author

let review b = match b with
  | {title="Peter F. Hamiltor"} -> "pretty good"
  | _ -> "Not so good"

let _ = review {author="Stephen King"; title="Gunslinger"; pages=768};;
(*
  Modules

  "The language of modules is distinct from the core language of types
  and expressions. It is concerned with program organization, not with
  computation itself." - ML for the Working Programmer

  The key parts of the module system in OCaml are:

  - Structures (~ value)
  - Signatures (~ type)
  - Functors   (~ functions)


*)


(*
  Structures - provide a way for grouping together related
  declarations like data types and functions the operate on them

  "If no module name is defined [...] it will implicitly be given a
  structure name derived from the file name"

  This is what I (perhaps a bit sloppy) called `namespaces` in the beginning.
*)

module Utils = struct
    let safe_div x y = if y == 0 then None else Some (x / y)
end

let _ = Utils.safe_div 3 0

(* Structures can be nested *)
module Utils = struct
    module IntUtils = struct
        let safe_div x y = if y == 0 then None else Some (x / y)
      end
    module StrUtils = struct
        let s = "MagickSTR1N6"
      end
end
let _ = Utils.StrUtils.s

(*
  Signatures - are the interfaces for structures

  It defines what parts of a structure should be visible from the outside.
  A signature can be used to hide components of a structure or export some definitions
  with more general types.

  Signatures are introduces with the sig keyword

*)
module type Set =
  sig
    type 't set
    val empty : 't set
    val member : 't set -> 't -> bool
    val insert : 't set -> 't -> 't set option
  end

(*
   Typically in OCaml you'll define your structure in one file `set.ml`
   and then create a second file `set.mli` which contains the signature.
*)


(*
  Functors (Not to be confused with anything else called functor)

  We said earlier that functors for modules are what functions are in
  the core language.

  In fact, functors are functions from structures to structures.

  This means that you can abstract over structures, similarly to what
  we did for types.
 *)


module type ORDERING =
  sig
    type t
    val compare : t -> t -> int
  end

module type MAX =
  sig
    type t
    val max : t list -> t
  end

module InstantiateMax (O : ORDERING) =
  struct
    type t = O.t
    let max ys =
      let rec max_acc xs ack = match xs with
          | [] -> ack
          | x :: xs' -> if O.compare x ack == 1 then max_acc xs' x
                        else max_acc xs' ack
      in match ys with
           | [] -> None
           | y :: ys -> Some (max_acc ys y)
  end

module IntOrdering =
  struct
    type t = int
    let compare = Pervasives.compare
  end

module IntMax = InstantiateMax(IntOrdering)

{% endhighlight %}
