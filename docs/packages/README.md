# packages

## Intro

A package is functionality being added to a threebot

## subdirs:

are subdirs of a package

- actors
    - is the logic inside a package
    - the code inside an actor should call as much as possible libraries in jumpscale (sals, clients, ...)
    - is also the implementation of our api for this package to the outside world, our interface basically
        - published  in webserver under: TO BE IMPLEMENTED
    - also published in gedis under namespace $packagename
    - each file inside is an actor
- chatflows
    - adds chatflow to http(s)://$threeboturl/$packagename/chatflow/$name
    - interactive communication, implemented as chat bots
    - each file inside is a chat bot
- models
    - the models used in a package, is j.data.schema ...
    - each file inside is a schema
- docsites
    - markdown documentation sites, published under /wiki/$docsite_prefix/...
    - each subdir is a docsite
- docmacros
    - macro's as used in docsite(s)
    - each file inside is a docmacro (can be in subdirs)
- wiki
    - adds wiki to http(s)://$threeboturl/$packagename/wiki
    - how to use wiki see ...jumpscaleX_threebot/docs
- html
    - adds html in http(s)://$threeboturl/$packagename/ so there could be an index
    - how to use wiki see ...jumpscaleX_threebot/docs     

all of these are optional and other loading logic can be used
they will be automatically loaded, do not do manually



