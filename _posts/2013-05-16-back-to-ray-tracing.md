---
layout: post
title: Back to Ray Tracing

---

Ten years ago or so, I was heavily into [Ray Tracing](http://en.wikipedia.org/wiki/Ray_tracing_%28graphics%29), trying out different rendering techniques and reading almost everything I could find about the topic. And suddenly, as life would have it, I got immersed with entirely different things and my rendering interest was put on hold...

## LEGO
Last weekend my family and I was visiting one of my oldest friends Oscar and his family. It turns out that Oscar has gotten really into [LEGO](http://http://www.lego.com/) and is a proud [AFOL](http://en.wiktionary.org/wiki/AFOL) and has been spending a lot of his spare time doing either virtual LEGO creations in [Lego Digital Designer](http://ldd.lego.com/)(LDD) (Really, if you like LEGO, you should try it out!) or building them out with actual bricks. 
Inspired by the LEGO renderings Oscar had been making using [POV-Ray](http://www.povray.org/) I got really excited about pulling out my old rendering code. Who knows, perhaps I could even write an interface to LDD, so that Oscar and others could use it as well.

## Looking at old code

It is kind of scary to go back to old code. Does the old code look like crap, and is it usable at all? Luckily, I did spend a lot of time in that particular code base, so it wasn't bad, apart maybe, from all [hungarian notation](http://en.wikipedia.org/wiki/Hungarian_notation) in the variable names. 

The project was originally built in Visual Studio, so I thought porting it to my Mac could be somewhat time consuming. That turned out to be really simple. Just fixing some relative include paths, a couple of class forward references and struggling a bit with a ``Makefile`` and I was up and running! 

## OpenMP

But man, it was sooo slow. When computing indirect light (Global Illumination) the idea is to sample the sourrounding environment with lots of samples -- and this is costly. Especially if you have a world consisting of hundreds of thousands of triangles. Furthermore, back in 2003, multi-core processors wasn't that common (I certainly didn't have one), so the code just ran in a single thread.

The first time I saw [OpenMP](http://en.wikipedia.org/wiki/OpenMP) used was in another rendering project, [smallpt](http://www.kevinbeason.com/smallpt/) - a Path Tracer in 99 lines of code. Check it out, it is a really cool project. Ray tracing in general is extremely suitable to parallelize, since it doesn't require much coordination between threads. The following code is literally my new code for making it run in parallel. I was actually surprised it worked on the first attempt.

{% highlight c++ %}
    #pragma omp parallel for schedule(dynamic, 1)
    for (int line=0; line < HEIGHT; ++line) {
        rt.renderNext(line);
    }
{% endhighlight %}

I'm definitely going to look more at OpenMP. I'm especially interested in how things work out when there is more coordination going on. 

## A couple of images

![Teapots](/img/pots.png)
![Lego formula 1](/img/f1.png)
![Sponza Atrium](/img/sponza.png)

## Resources on Ray Tracing 
There are probably a lot of good resources online, but I think I have learned the most from a couple of books:

- [Shirley - Realistic Ray Tracing](http://www.amazon.com/Realistic-Ray-Tracing-Peter-Shirley/dp/1568814615)
- [Dutre, Bekaert, Bala - Advanced Global Illumination](http://www.amazon.com/Advanced-Global-Illumination-Second-Philip/dp/1568813074)
- [Wann Jensen - Realistic Image Synthesis Using Photon Mapping](http://www.amazon.com/Realistic-Image-Synthesis-Photon-Mapping/dp/1568811470) 





