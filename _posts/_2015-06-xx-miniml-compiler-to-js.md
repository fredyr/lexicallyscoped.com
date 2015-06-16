---
layout: post
title: OCaml - Compiling Mini-ML to Javascript

---

> If you don't know OCaml, or want to brush up on the
> syntax, you can check out my [Introduction to OCaml]()-page


## What is Mini-ML ##

Mini-ML is a small subset of ML, more specifically a simple typed
lambda-calculus with constants, products, conditional, and recursive
function definitions. For more background information on Mini-ML, see
[A Simple Applicative Language: Mini-ML]() (Clement) and
[Computation and Deduction]() (Pfenning).

For our purpose, I like a more informal definition: a programming
language, powerful enough to be interesting, while still being small
enough to be possible to implement a compiler or interpreter for.

The variant of Mini-ML that we shall take a closer look at is
implemented on the excellent
[The Programming Language Zoo](http://andrej.com/plzoo/) page by
[Andrej Bauer](http://andrej.com/). Besides having a Mini-ML compiler
and interpreter, you can also find a Mini-Haskell implementation
(lazy, purely functional language) and a Mini-prolog. I definitely
recommend you to check them out!

Another similar project, albeit a bit more ambitious is the
[MinCaml compiler](https://github.com/esumii/min-caml), an educational
compiler for a minimal subset of OCaml, written in ~2000 lines of
OCaml. It has been used for teaching at the University of Tokyo. The
paper presenting it is a nice introduction: [MinCaml: A Simple and
Efficient Compiler for a Minimal Functional Language](http://esumii.github.io/min-caml/paper.pdf)

## Syntax of Mini-ML

We going to look at, and play around with the Mini-ML code from the
Programming Language Zoo page to start with. Here is the [link]()
again. We going to start off with the syntax, (Syntax.ml) and then use
the Lexer.ml and Parser.ml

In Mini-ML we have the following constructs.

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

Here is how all the aboe expressions are represented in the abstract
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



{% highlight ocaml %}

let str = "35;; fun f(x : int) : int is x + 3;;let b = if true then -1 else 1;;"
let x = Lexer.token (Lexing.from_string str)
let cmds = Parser.toplevel Lexer.token (Lexing.from_string str)

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

let compile_toplevel = function
  | Expr e     -> (compile_expr e) ^ ";\n"
  | Def (n, e) -> "var " ^ n ^ " = " ^ (compile_expr e) ^ ";\n"

let _ = print_string @@ List.fold_left (fun js cmd -> js ^ compile_toplevel cmd) "" cmds

{% endhighlight %}


----
Additional stuff I might include some more?


TODO: should i use the type checker to check. could work straight away
since the miniml isn't changed?
- Show examples on runnning type checking on some expressions


Talk about Purescript being similar to haskell, but embracing the
semantics of Javascript. This could be done in a MiniML language that
compiles to js. PAttern matching, row type polymorpism.
