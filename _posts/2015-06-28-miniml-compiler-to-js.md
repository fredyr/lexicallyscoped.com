---
layout: post
title: OCaml - Compiling Mini-ML to Javascript

---

> If you don't know OCaml, or want to brush up on the
> syntax, you can check out my [Introduction to OCaml](/2015/06/06/intro-to-ocaml.html)-page


## What is Mini-ML? ##

Mini-ML is a small subset of ML, more specifically a simple typed
lambda-calculus with constants, products, conditional, and recursive
function definitions. For more background information on Mini-ML, see

- [A Simple Applicative Language: Mini-ML](https://hal.inria.fr/inria-00076025/file/RR-0529.pdf) (Clement)
- [Computation and Deduction](http://www.cs.cmu.edu/~twelf/notes/cd.pdf) (Pfenning)

For our purpose, I like a more informal definition: a programming
language, powerful enough to be interesting, while still being small
enough to be possible to implement a compiler or interpreter for.

The variant of Mini-ML that we shall take a closer look at is
implemented on the excellent
[The Programming Language Zoo](http://andrej.com/plzoo/) page by
[Andrej Bauer](http://andrej.com/). Besides having a Mini-ML compiler
and interpreter, you can also find a Mini-Haskell implementation
(lazy, purely functional language) and a Mini-Prolog. I definitely
recommend you to check them out!

### Similar project

Another similar project, albeit more ambitious is the
[MinCaml compiler](https://github.com/esumii/min-caml), an educational
compiler for a minimal subset of OCaml, written in ~2000 lines of
OCaml. It has been used for teaching at the University of Tokyo. Their
paper is a nice introduction: [MinCaml: A Simple and
Efficient Compiler for a Minimal Functional Language](http://esumii.github.io/min-caml/paper.pdf)

### Compiling full OCaml to Javascript
If your interested in using OCaml for web related projects, you can check out
[Js_of_ocaml](http://ocsigen.org/js_of_ocaml/), which makes it
possible to run OCaml in the browser.


## Syntax of Mini-ML

We going to look at, and play around with the Mini-ML code from the
Programming Language Zoo page to start with. Here's the direct
[Mini-ML link](http://andrej.com/plzoo/html/miniml.html). We going to
start off with the syntax, (`syntax.ml`) and then look at the parser and
lexer (`lexer.mll`/`parser.mly`).

### Mini-ML constructs

Constant literals for integers and booleans.
{% highlight ocaml %}
123;;
5;;
true;;
false;;
{% endhighlight %}

We can compose these literals into expressions using the following operators.
{% highlight ocaml %}
12 * 43;; (* => 516 *)
9 + 33;;  (* => 42 *)
42 - 11;; (* => 31*)
4 = 3;;   (* => false *)
2 < 3;;   (* => true *)
{% endhighlight %}

And finally, let-definitions, conditional statements, function definitions and function application.
{% highlight ocaml %}
let a = true;;
let b = if a then -1 else 1;;

(* Functions requires explicit type declarations *)
fun addthree(x : int) : int is x + 3;;

let c = addthree 4 + addthree 2;;
{% endhighlight %}

## Abstract Syntax Tree

Here is how all the above expressions are represented in the abstract
syntax tree (`Syntax.ml`).
{% highlight ocaml %}

(* Variable names *)
type name = string

(* Types *)
type ty =
  | TInt              (* Integers *)
  | TBool             (* Booleans *)
  | TArrow of ty * ty (* Functions *)

(* Expressions *)
type expr =
  | Var of name                          (* Variable *)
  | Int of int                           (* Non-negative integer constant *)
  | Bool of bool                         (* Boolean constant *)
  | Times of expr * expr                 (* Product [e1 * e2] *)
  | Plus of expr * expr                  (* Sum [e1 + e2] *)
  | Minus of expr * expr                 (* Difference [e1 - e2] *)
  | Equal of expr * expr                 (* Integer comparison [e1 = e2] *)
  | Less of expr * expr                  (* Integer comparison [e1 < e2] *)
  | If of expr * expr * expr             (* Conditional [if e1 then e2 else e3] *)
  | Fun of name * name * ty * ty * expr  (* Function [fun f(x:s):t is e] *)
  | Apply of expr * expr                 (* Application [e1 e2] *)

(* Toplevel commands *)
type toplevel_cmd =
  | Expr of expr       (* Expression *)
  | Def of name * expr (* Value definition [let x = e] *)
{% endhighlight %}

You can see we have datatypes for

- Types
- Expressions
- Toplevel commands

where the toplevel commands can be either a binding of an expression
to a name, or just a plain expression.

With these datatypes, we're able to create representations of all the code examples
we've seen above, in OCaml code. Here are a couple of examples.

{% highlight ocaml %}
open Syntax (* We open the Syntax module, so we don't have to prefix everything with Syntax.Int etc *)


let int_lit = Int 123
let prod_expr = Times (Int 12, Int 43)
let cmp = Less (Int 2, Int 3)

let toplevel_def = Def ("b", If (Var "a", Int ~-1, Int 1))

let fn = Fun ("addthree", "x", TInt, TInt, Plus (Var "x", Int 3))
{% endhighlight %}

## Parsing and lexing

The lexer and parser can already create these data structures for us.
They are built via OCamllex and Ocamlyacc ([Lexer and parser generators](http://caml.inria.fr/pub/docs/manual-ocaml-4.00/manual026.html)). If you want to learn more
about how these work, and maybe add some features of your own to
Mini-ML, the [Real World OCaml book has a good chapter](https://realworldocaml.org/v1/en/html/parsing-with-ocamllex-and-menhir.html) on parsing and
lexing. They also use [Menhir](http://gallium.inria.fr/~fpottier/menhir/) instead of OCamlyacc, which is
recommended for any serious parsing. (See the discussion on Menhir vs.
OCamlyacc in the Real World OCaml chapter linked.)

First we'll generate our parser and lexer from the definitions inside the files `lexer.mll` and `parser.mly`.

{% highlight ocaml %}
ocamllex lexer.mll   (* Creates `lexer.ml` *)
ocamlyacc parser.mly (* Creates `parser.ml` *)
{% endhighlight %}


## Pass a string, get an AST

Let's put the lexer and parser to use.

We'll try the lexer first, with a simple string containing two expressions.
{% highlight ocaml %}
let str =
  "35 < 423;;
   let a = true;;"
{% endhighlight %}

From the string we create a
[lexer buffer](http://caml.inria.fr/pub/docs/manual-ocaml/libref/Lexing.html).

{% highlight ocaml %}
let lexbuf = Lexing.from_string str
{% endhighlight %}

The lexer buffer is stateful, and you can pluck tokens from it at will.
{% highlight ocaml %}
let _ = Lexer.token lexbuf;;
(* - : Parser.token = Parser.INT 35 *)
let _ = Lexer.token lexbuf;;
(* - : Parser.token = Parser.LESS *)
let _ = Lexer.token lexbuf;;
(* - : Parser.token = Parser.INT 423 *)
let _ = Lexer.token lexbuf;;
(* - : Parser.token = Parser.SEMICOLON2 *)
let _ = Lexer.token lexbuf;;
(* - : Parser.token = Parser.LET *)
{% endhighlight %}

But we can also just send the lexer buffer straight into the parser,
and out we get the abstract syntax tree!

{% highlight ocaml %}
let cmds = Parser.toplevel Lexer.token (Lexing.from_string str)

(* val cmds : toplevel_cmd list =
  [Expr (Less (Int 35, Int 423)); Def ("a", Bool true)] *)
{% endhighlight %}

## Type checking
With the type checker (`type_check.ml`) you can verify that
expressions have a certain type.

{% highlight ocaml %}
let _ = Type_check.check [] TBool (Int 35)

(* Exception:
Type_check.Type_error "35 has type int but is used as if it has type bool". *)
{% endhighlight %}

Or you can infer the type of an expression.

{% highlight ocaml %}
let _ = Type_check.type_of [] (Int 34)
(* - : ty = TInt *)

let _ = Type_check.type_of [("a", TBool)] @@ If (Var "a", Int ~-1, Int 1)
(* - : ty = TInt *)
{% endhighlight %}

## Compiling to Javascript

The actual compilation step from the abstract syntax tree into
Javascript is very simple. We generate a piece of Javascript
for each type of expression. To make it simple, we generate strings
containing Javascript code directly.

{% highlight ocaml %}
let rec compile_expr = function
  | Var n -> n
  | Int i -> string_of_int i
  | Bool b -> string_of_bool b
  | Times (e1, e2) -> (compile_expr e1) ^ " * " ^ (compile_expr e2)
  | Plus  (e1, e2) -> (compile_expr e1) ^ " + " ^ (compile_expr e2)
  | Minus (e1, e2) -> (compile_expr e1) ^ " - " ^ (compile_expr e2)

  | Equal (e1, e2) -> (compile_expr e1) ^ " === " ^ (compile_expr e2)
  | Less (e1, e2) -> (compile_expr e1) ^ " < " ^ (compile_expr e2)
  | If (e1, e2, e3) -> "(function(){ if(" ^ (compile_expr e1)
                       ^ ") return (" ^ (compile_expr e2)
                       ^ "); else return (" ^ (compile_expr e3)
                       ^ ");})()"
  | Apply (f, x) -> "(" ^ (compile_expr f) ^ ")(" ^ (compile_expr x) ^ ")"
  | Fun (f, x, _,  _, e) ->
     "function " ^ f ^ "(" ^ x ^ ") { return " ^ (compile_expr e) ^ ";}"
{% endhighlight %}

We recursively generate Javascript for all expressions. Since
`if`-statements in Mini-ML (and OCaml) are expressions, meaning they
return a value, the generated Javascript is encapsulated with an
anonymous function that is applied directly. This makes the generated
Javascript return a value for an `if`-expression.

The compilation of toplevel commands is similar.
{% highlight ocaml %}
let compile_toplevel = function
  | Expr e     -> (compile_expr e) ^ ";\n"
  | Def (n, e) -> "var " ^ n ^ " = " ^ (compile_expr e) ^ ";\n"
{% endhighlight %}

## Showtime: Javascript output
Let's look at the results.

{% highlight ocaml %}
let _ = print_string @@ List.fold_left (fun js cmd -> js ^ compile_toplevel cmd) "" cmds

(*
35 < 423;
var a = true;
*)
{% endhighlight %}

Yay, it works! But it is not the most interesting example. Let's test
some more.

{% highlight ocaml %}
let str =
  "35 < 423;;
   let a = true;;
   fun addthree(x : int) : int is x + 3;;
   let c = addthree 4 + addthree 2;;
   let b = if a then -1 else 1;;"

let cmds = Parser.toplevel Lexer.token (Lexing.from_string str)
let _ = print_string @@ List.fold_left (fun js cmd -> js ^ compile_toplevel cmd) "" cmds

(*
35 < 423;
var a = true;
function addthree(x) { return x + 3;};
var c = (addthree)(4) + (addthree)(2);
var b = (function(){ if(a) return (-1); else return (1);})();
*)
{% endhighlight %}

Of course, we can't finish this without including our good old friend
fibonacci!

I hope you've enjoyed this as much as I did making it. If you have any
comments or feedback, don't hesitate to send me an
[email](mailto:fredrik.dyrkell@gmail.com) or a message on Twitter
[@lexicallyscoped](https://twitter.com/lexicallyscoped).

{% highlight ocaml %}
let str =
  "fun fib(x : int) : int is
     if x < 2 then 1
     else x * fib (x - 1);;
   let big = fib(10);;"

let cmds = Parser.toplevel Lexer.token (Lexing.from_string str)
let _ = print_string @@ List.fold_left (fun js cmd -> js ^ compile_toplevel cmd) "" cmds

(*
function fib(x) { return (function(){ if(x < 2) return (1); else return (x * (fib)(x - 1));})();};
var big = (fib)(10);
*)
{% endhighlight %}
