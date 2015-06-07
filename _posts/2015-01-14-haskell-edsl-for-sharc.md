---
layout: post
title: Writing a domain specific language for Sharc assembly in Haskell

---

### Domain Specific Languages in Haskell ###

I made a presentation at one of our [local meetup groups](https://twitter.com/GotLambda) earlier this
fall. Here's my (text-based) slides from that presentation. It was an
interactive presentation, so most of the code examples are meant to be
evaluated when following along.

---

### DOMAIN SPECIFIC LANGUAGE (DSL)
a computer programming language of limited expressiveness focussed
on a particular domain

-- Martin Fowler

A very good paper on Domain Specific Languages in Haskell is:
[Functional Programming for Domain-Specific Languages](http://www.comlab.ox.ac.uk/jeremy.gibbons/publications/fp4dsls.pdf)
by [Jeremy Gibbons](http://www.cs.ox.ac.uk/jeremy.gibbons/)

More reading material on Domain Specific Languages can be found on
[haskell.org](http://www.haskell.org):

- [Research papers on Domain Specific Languages](https://www.haskell.org/haskellwiki/Research_papers/Domain_specific_languages)
- [Embedded Domain Specific Languages](https://www.haskell.org/haskellwiki/Embedded_domain_specific_language)

---

# A LITTLE BACKGROUND

Two main approaches to implementing DSLs

1. Stand-alone language
   - Custom syntax, that can be tailored for the domain 
   - Requires building parser, compiler etc -> Significant work 

2. Embedded DSL
   - Leverages syntax and abstractions from a host language
   - The DSL is a library defining the domain specific semantic
   - Blurres the boundary between the host and DSL


We're going to look at a specific form called *deeply embedded* DSL
so called because terms in the DSL are implemented simply to
construct and abstract syntax tree (AST).

---

Using Haskell's
[Algebraic Datatypes (ADT)](http://en.wikipedia.org/wiki/Algebraic_data_type)
we can create ASTs like so

{% highlight haskell %}
data DExp = LitInt Int 
          | Add DExp DExp
          | Sub DExp DExp
          | Mul DExp DExp
          | LitBool Bool
            deriving Show
{% endhighlight %}

A value of the `DExp` type can be created with one of the above
*constructor functions*, for example the constructor function `LitInt` takes an Integer
as argument.

{% highlight haskell %}
LitInt 5
:t LitInt -- => LitInt :: Int -> DExp
 
Add (LitInt 4) (LitInt 12)
:t LitBool True
{% endhighlight %}

Use functions and/or operators for construction. For example we can
implement the Num type class.

{% highlight haskell %}
:i Num
-- =>
class Num a where
  (+) :: a -> a -> a
  (*) :: a -> a -> a
  (-) :: a -> a -> a
  negate :: a -> a
  abs :: a -> a
  signum :: a -> a
  fromInteger :: Integer -> a
{% endhighlight %}


{% highlight haskell %}
instance Num DExp where
  a + b = Add a b
  a - b = Sub a b
  a * b = Mul a b
  fromInteger i = LitInt $ fromInteger i
{% endhighlight %}


{% highlight haskell %}
-- Let's try out some expressions
1+4*9 :: DExp
Mul 4 5
{% endhighlight %}

Add a couple of functions.

{% highlight haskell %}
sqr x = x * x
conjugate a b = sqr a - sqr b

-- And try them out
sqr 4
sqr 4 :: DExp
sqr $ 1+4*9 :: DExp
conjugate (9*3) (4-1) :: DExp
{% endhighlight %}


This DSL is *unityped* - everything is `DExp`, which means its
possible to construct illegal ASTs.

{% highlight haskell %}
Mul (LitBool True) 1 -- Bad
{% endhighlight %}

---

### INTERPRET ALL THE THINGS 

Pattern match on the different constructor functions and voila
{% highlight haskell %}
eval :: DExp -> Int
eval (LitInt a) = a
eval (Add a b)  = (eval a) + (eval b)
eval (Sub a b)  = (eval a) - (eval b)
eval (Mul a b)  = (eval a) * (eval b)
{% endhighlight %}

{% highlight haskell %}
-- Try these out yourself in the REPL
eval (LitInt 4)
eval (2+6*4 :: DExp)
eval (conjugate (9*7) (4-2) :: DExp)
{% endhighlight %}

---


But you can just as easily

### COMPILE ALL THE THINGS

{% highlight haskell %}
data Asm = Push Int | StackAdd | StackSub | StackMul
         deriving Show

genByteCode :: DExp -> [Asm]
genByteCode (LitInt a) = [Push a]
genByteCode (Add a b)  = (genByteCode a) ++ (genByteCode b) ++ [StackAdd]
genByteCode (Sub a b)  = (genByteCode a) ++ (genByteCode b) ++ [StackSub]
genByteCode (Mul a b)  = (genByteCode a) ++ (genByteCode b) ++ [StackMul]
{% endhighlight %}


{% highlight haskell %}
-- Examples
genByteCode (12 + sqr 4 -sqr 2 * 3)
genByteCode $ conjugate (9*7) (4-2)
{% endhighlight %}

---

### SWITCHING GEARS A LITTLE BIT

Has anybody here done any assembly language coding?

I currently do consulting work for a client, working with embedded
systems. Here I have been introduced to the
[SHARC processor](http://www.analog.com/en/processors-dsp/sharc/products/index.html)
and its [assembly language](https://www.danvillesignal.com/developers-links-resources/sharc-developer-links).

#### Registers
- R0-R15 Fixed point (Integer) 
- F0-F15 Floating point

#### Algebraic notation
{% highlight haskell %}
R1 = R2 + R3;
F2 = F0 * F1;
F9 = MIN(F2, F14);
F3 = F2 - F1;
{% endhighlight %}

With a DSL implementation of the SHARC assembly language you could
explore interesting things like:

1. Faster feedback-loop, since you can run (interpret) code on your
   machine directly and not run on actual hardware. 
2. Use Haskell to create abstractions on top of the assembly,
   advance macros.
3. Quickcheck testing and unit testing - Isolation testing an
   assembly function is a PITA.

---

{% highlight haskell %}
data Rx = R0 | R1 | R2 | R3 | R4 | R5 | R6 | R7
        | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15
        deriving (Show, Eq, Ord) 
data Fx = F0 | F1 | F2 | F3 | F4 | F5 | F6 | F7
        | F8 | F9 | F10 | F11 | F12 | F13 | F14 | F15
        deriving (Show, Eq, Ord)
{% endhighlight %}

The SHARC asm is strongly typed, you can't mix Rx and Fx registers.
Illegal examples:
{% highlight haskell %}
R2 = R0 + F1
F0 = R0 + R1
{% endhighlight %}

Both the expression on the rhs must be correctly typed, as well as the
assignment.

We want the AST to only contain *legal* constructions.
This is possible using Generalized Algebraic Data Types (GADTs).

`Expr` is now a polymorpic type, but *only* provides constructor
functions for `Expr Integer` and `Expr Float` and not for other
instances of the polymorphic type `Expr a`.

{% highlight haskell %}
data Expr :: * -> * where
  LiteralInt   :: Integer -> Expr Integer
  AddR         :: Rx -> Rx -> Expr Integer
  LiteralFloat :: Float -> Expr Float
  AddF         :: Fx -> Fx -> Expr Float
{% endhighlight %}

{% highlight haskell %}
:t LiteralInt 3
:t LiteralFloat 4.9
:t AddF F0 F1
:t AddF F0 R1
{% endhighlight %}

### THE SHARC ASM DSL

Here's the whole shebang to play around with. Happy DSL hacking!

{% highlight haskell %}
{-#LANGUAGE GADTs, KindSignatures, FlexibleInstances, FunctionalDependencies, NoMonomorphismRestriction #-}
{-# LANGUAGE CPP #-}

import Control.Monad.State (State, execState, get, put, modify) 
import qualified Data.Map as M
import qualified Data.Bits as B

infix 4 <~
infixl 6 +.
infixl 6 -.
infixl 6 *.

data Rx = R0 | R1 | R2 | R3 | R4 | R5 | R6 | R7
        | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15
        deriving (Show, Eq, Ord) 
data Fx = F0 | F1 | F2 | F3 | F4 | F5 | F6 | F7
        | F8 | F9 | F10 | F11 | F12 | F13 | F14 | F15
        deriving (Show, Eq, Ord)
data Ix = I0 | I1 | I2 | I3 | I4 | I5 | I6 | I7
        | I8 | I9 | I10 | I11 | I12 | I13 | I14 | I15
        deriving (Show, Eq, Ord) 
data Mx = M0 | M1 | M2 | M3 | M4 | M5 | M6 | M7
        | M8 | M9 | M10 | M11 | M12 | M13 | M14 | M15
        deriving (Show, Eq, Ord)
data Cond = Eq | Ne | Gt | Lt | Ge | Le deriving (Show, Eq, Ord)

data Expr :: * -> * where
  LitInt :: Integer -> Expr Integer
  RegR   :: Rx -> Expr Integer
  AddR   :: Rx -> Rx -> Expr Integer
  SubR   :: Rx -> Rx -> Expr Integer
  MulR   :: Rx -> Rx -> Expr Integer
  MinR   :: Rx -> Rx -> Expr Integer
  MaxR   :: Rx -> Rx -> Expr Integer
  AndR   :: Rx -> Rx -> Expr Integer
  OrR    :: Rx -> Rx -> Expr Integer
  XorR   :: Rx -> Rx -> Expr Integer
  NegR   :: Rx -> Expr Integer
  NotR   :: Rx -> Expr Integer
  AbsR   :: Rx -> Expr Integer
  PassR  :: Rx -> Expr Integer
  IncR   :: Rx -> Expr Integer
  DecR   :: Rx -> Expr Integer

  LitFloat :: Float -> Expr Float
  RegF     :: Fx -> Expr Float
  AddF     :: Fx -> Fx -> Expr Float
  SubF     :: Fx -> Fx -> Expr Float
  MulF     :: Fx -> Fx -> Expr Float
  MinF     :: Fx -> Fx -> Expr Float
  MaxF     :: Fx -> Fx -> Expr Float
  NegF     :: Fx -> Expr Float
  AbsF     :: Fx -> Expr Float
  PassF    :: Fx -> Expr Float

  RegI :: Ix -> Expr Integer
  RegM :: Mx -> Expr Integer

-- By completely separating AddF from AddR we only allow the type safe
-- constructions

instance Show (Expr Integer) where
  show s' = case s' of
    LitInt n -> show n
    RegR n -> show n
    RegI n -> show n
    RegM n -> show n
    AddR a b -> show a ++ "+" ++ show b
    SubR a b -> show a ++ "-" ++ show b
    MulR a b -> show a ++ "*" ++ show b
    MinR a b -> "MIN(" ++ show a ++ "," ++ show b ++ ")"
    MaxR a b -> "MAX(" ++ show a ++ "," ++ show b ++ ")"
    AndR a b -> show a ++ " AND " ++ show b
    OrR a b -> show a ++ " OR " ++ show b
    XorR a b -> show a ++ " XOR " ++ show b
    NegR a -> "-" ++ show a
    NotR a -> "NOT " ++ show a 
    AbsR a -> "ABS " ++ show a 
    PassR a -> "PASS " ++ show a 
    IncR a -> show a ++ "+1"
    DecR a -> show a ++ "-1"

instance Show (Expr Float) where
  show s' = case s' of
    LitFloat n -> show n
    RegF n -> show n
    AddF a b -> show a ++ "+" ++ show b
    SubF a b -> show a ++ "-" ++ show b
    MulF a b -> show a ++ "*" ++ show b
    MinF a b -> "MIN(" ++ show a ++ "," ++ show b ++ ")"
    MaxF a b -> "MAX(" ++ show a ++ "," ++ show b ++ ")"
    NegF a -> "-" ++ show a
    AbsF a -> "ABS " ++ show a
    PassF a -> "PASS " ++ show a

-- Custom implementation of Show for the Expr allows for printing the
-- AST in the form the `real` assembly lang would look like 
-- > AddR R9 R10
-- > MinF F0 F1

data Stmt where 
  AssignR    :: Rx -> Expr Integer -> Stmt 
  AssignF    :: Fx -> Expr Float -> Stmt 
  AssignI    :: Ix -> Expr Integer -> Stmt
  AssignM    :: Mx -> Expr Integer -> Stmt

  ModifyReg  :: Ix -> Mx -> Stmt
  ModifyIm   :: Ix -> Integer -> Stmt
  Para       :: SharcProgram -> Stmt 

-- Statements enforces the same restrictions, only Rx registers can be
-- assigned an Integer Expr and so on

instance Show Stmt where
  show s' = case s' of
    AssignR r e -> show r ++ "=" ++ show e
    AssignF r e -> show r ++ "=" ++ show e
    AssignI r e -> show r ++ "=" ++ show e
    AssignM r e -> show r ++ "=" ++ show e
    ModifyReg i m -> "MODIFY(" ++ show i ++ "," ++ show m ++ ")"
    ModifyIm  i m -> "MODIFY(" ++ show i ++ "," ++ show m ++ ")"
    Para l -> "[" ++ show l ++ "]"

-- Previous examples in AST form
-- > AssignR R1 $ AddR R2 R3
-- > AssignF F2 $ MulF F0 F1
-- > AssignF F9 $ MinF F2 F14
-- > AssignF F3 $ SubF F2 F1

-- Illegal examples
-- AssignR R2 $ AddR R0 F1
-- AssignF F0 $ AddR R0 R1

-- FROM NOW ON ITS JUST ABOUT SYNTAX AND CONVENIENCE
--

class ALU a b | a -> b where
  add  :: a -> a -> b
  sub  :: a -> a -> b
  mul  :: a -> a -> b
  min_ :: a -> a -> b 
  max_ :: a -> a -> b
  neg  :: a -> b
  abs_ :: a -> b
  pass :: a -> b

-- Polymorphic type class to be able to use the same operators on both
-- Rx and Fx

instance ALU Rx (Expr Integer) where
  add m n   = AddR m n
  sub m n   = SubR m n
  mul m n   = MulR m n
  min_ m n  = MinR m n
  max_ m n  = MaxR m n
  neg m     = NegR m
  abs_ m    = AbsR m
  pass m    = PassR m

instance ALU Fx (Expr Float) where
  add m n   = AddF m n
  sub m n   = SubF m n
  mul m n   = MulF m n
  min_ m n  = MinF m n
  max_ m n  = MaxF m n
  neg m     = NegF m
  abs_ m    = AbsF m
  pass m    = PassF m

class Asgn l r where
  (<~) :: l -> r -> Sharc ()

class Mdfy m where
  modify_ :: Ix -> m -> Sharc ()

instance Asgn Rx (Expr Integer) where
  (<~) r e = addStmt $ AssignR r e

instance Asgn Fx (Expr Float) where
  (<~) r e = addStmt $ AssignF r e

instance Asgn Rx Rx where
  (<~) r s = addStmt $ AssignR r $ RegR s 

instance Asgn Fx Fx where
  (<~) r s = addStmt $ AssignF r $ RegF s 

instance Asgn Ix Ix where
  (<~) r s = addStmt $ AssignI r $ RegI s 

instance Asgn Mx Mx where
  (<~) r s = addStmt $ AssignM r $ RegM s 

instance Asgn Rx Integer where
  (<~) r i = addStmt $ AssignR r $ LitInt i 

instance Asgn Fx Float where
  (<~) r f = addStmt $ AssignF r $ LitFloat f

instance Asgn Ix Integer where
  (<~) r i = addStmt $ AssignI r $ LitInt i 

instance Asgn Mx Integer where
  (<~) r i = addStmt $ AssignM r $ LitInt i 

instance Mdfy Mx where
  modify_ i m = addStmt $ ModifyReg i m 
instance Mdfy Integer where
  modify_ i m = addStmt $ ModifyIm i m 

and_ x y = AndR x y
or_  x y = OrR x y
xor_ x y = XorR x y
not_ x   = NotR x

inc x   = IncR x
dec x   = DecR x
(+.) = add
(-.) = sub
(*.) = mul

type SharcProgram = [Stmt]
type Sharc = State (Int, SharcProgram)

addStmt :: Stmt -> Sharc ()
addStmt a = modify $ \ (n, p) -> (n, p ++ [a])

assemble :: Sharc () -> SharcProgram
assemble program = snd $ execState program (0, [])

#define APRIME 11
#define SIX 6

fun :: Sharc ()
fun = do
  R1 <~ (APRIME::Integer) 
  R2 <~ (6::Integer) 
  R0 <~ R1
  R2 <~ R1 +. R2
  R3 <~ R1 *. R2
  R5 <~ min_ R1 R2
  R6 <~ max_ R1 R2
  R4 <~ R1
  R7 <~ neg R4
  R8 <~ abs_ R4
  R9 <~ R1 `and_` R2
  R9 <~ and_ R1 R2

-- State monad jiggery pokery to get the nice do syntax
-- With the assemble function we run through the state and accumulate
-- all instructions into a list, aka the COMPILER

-- OR A SMALL INTERPRETER (only integer parts now :s) 

type Env = M.Map Rx Integer
initialEnv = M.fromList [(R0, 0), (R1, 0), (R2, 0)]

eval :: Env -> Stmt -> Env
eval env (AssignR r expr) = M.insert r (evalExpr env expr) env

evalExpr :: Env -> Expr Integer -> Integer
evalExpr _   (LitInt i)   = i
evalExpr env (RegR r)   = env M.! r
evalExpr env (AddR r s) = (env M.! r) + (env M.! s)
evalExpr env (SubR r s) = (env M.! r) - (env M.! s)
evalExpr env (MulR r s) = (env M.! r) * (env M.! s) 
evalExpr env (MinR r s) = min (env M.! r) (env M.! s) 
evalExpr env (MaxR r s) = max (env M.! r) (env M.! s) 
evalExpr env (NegR r)   = -(env M.! r)
evalExpr env (AbsR r)   = abs $ env M.! r
evalExpr env (IncR r)   = (env M.! r) + 1
evalExpr env (DecR r)   = (env M.! r) - 1
evalExpr env (AndR r s) = (env M.! r) B..&. (env M.! s)
evalExpr env (OrR r s)  = (env M.! r) B..|. (env M.! s)
evalExpr env (XorR r s) = B.xor (env M.! r) (env M.! s)
evalExpr env (NotR r)   = B.complement (env M.! r) 

run = foldl eval initialEnv (assemble fun)

{% endhighlight %}



If you have any comments or feedback,
send me an [email](mailto:fredrik.dyrkell@gmail.com) or send me a message on
Twitter [@lexicallyscoped](https://twitter.com/lexicallyscoped).


