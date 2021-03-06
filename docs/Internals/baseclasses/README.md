# JSX Baseclasses

## Index
- [Intro](#intro)
- [Baseclasses](#base-classes)
    - [JSBase](#jsbase-class)
    - [JSAttr](#jsattr-class)
    - [JSDict](#jsdict-class)
    - [JSConfigsBCDB](#jsconfigsbcdb-class)
    - [JSConfigBCDBBasse](#jsconfigbcdbbase-class)
    - [JSConfigBCDB](#jsconfigbcdb-class)
    - [JSFactory](#jsfactory-class)
    - [JSFactoryData](#jsfactorydata-class)
    - [ThreeBotPackageBase](#threebotpackage-class)
    - [BuilderBaseClass](#builderbase-class) :

- [Jumpscale generated](#jumpscale-generated)
- [See More](#see-more)

## Intro
BaseClasses are the parent of everything like config manager, clients, builders, servers,packages .. etc.

Also they contain a lot of functions to help in logging, caching, auto completion in shell, config manager instance managment.

Simply if I need to know where a client comes from:<br>
- The top parent class will be `JSBase` class.
- The factory (which has the base features for instances) inherits from `JSBaseConfigsBCDB` class and composes the client as a child class.
- The client (The instance) also inherits from `JSBaseConfigBCDB` 

### Properties available on all base classes:
- _location  : e.g. j.clients.ssh, is always the location name of the highest parent
- _name : name of the class itself in lowercase
- _key: is a unique key per object based on _location,_name and if relevant "name" of model inside, is used in the logger

We will go through the base classes available in detail in the next sections

## Base Classes
## JSBase Class:
### `j.baseclasses.object`
This is the baseclass used by all other base classes. It's in the lowest level. Every object in Jumpscale inherits from this one.

## JSAttr Class
Joins JSBase as a lower level class which objects inherit from. It deals with set & get attributes as well as with short names, via jumpscale generated.<br>

#### Methods:
- `__getattr__` : Gets class attriubte from child instances, doesn't return private or non child attributes


- `__setattr__`: Takes key, value and set's the instance attribute

## JSDict Class
### `j.baseclasses.dict`
Is an implementation of a dict in js.<br>

#### Methods:
- `_add` : Add item to the dict with name and value params
- `__len__` : Get number of items in the dict
- `__getitem__` : Get value of item by providing key
- `__delitem__` : Delete item(key and value) corresponding to the key provided
- `__setitem__` : Set an item by providing key and value to be set
- `__getattr__` : Get a property or item set in the dict class by providing the its name
- `__setitem__` : Set a property by providing its name and value

## JSConfigsBCDB Class:
### `j.baseclasses.object_config_collection`
This class is the factory for multiple JSConfig/JSConfigs baseclasses and its objects.
It contains some methods that help both of them to make the config manager. It deals directly with BCDB (Block chain database) always uses the system BCDB, unless if this one implements something else.

Can have a `__jslocation__`, meaning it will be attached somewhere in the Jumpscale namespace.

It can optionally be a container for one or more config classes, that is why it is not `_CHILDCLASS` here but `_CHILDCLASSES`.

The _CHILDCLASSES are one or more config(s) classes, always defined as a (Python) List.

A childclass can be a singleton (means just add a JSConfig class)

**Methods**
- `delete()`: deletes the instance (child object).
- `save()`: save new instance in bcdb with it's configurations.
- `find()`: find all instances(child object) created that satisfy filter options provided. eg: `find(color="red")`
- `count()`: count number of instances(child object) that satisfy filter options provided. eg: `find(color="red")`
- `exists()`: returns the existance(True of False) of the instance (child object)with the name provided

## JSCongfigBCDBBase Class:
### `j.baseclasses.object_config_base`
Is the base class for the object_config_collection (a collection of config objects) and object_config(config object), allowing you to create instances of the _CHILDCLASS on the fly (composition).

It has the base methods used in clients which deals with childclasses; creating, deleting, reseting, finding.

**Methods**
- `_bcdb_selector()`: select bcdb namespace, always uses the system BCDB, unless if this one implements something else.

- `_childclass_selector()`: allow custom implementation of which child class to use.

- `new()`: Create new config (instance) from a server, client must have a unique name and other configs could be entered later.

- `get()`: Gets an object from the instance.

- `exists()`: Checks if the instance already created.

- `reset()`: will destroy all data in the DB, will delete all existed instances.

- `find()`: Search for instance or list of instances by keys.

- `count()`: Count the child instances and return its length.

- `delete()`: Delete a specific instance.

## JSConfigBCDB Class:
### `j.baseclasses.object_config`
Is the base class for a config instance object could be a client, server, classes who use JSXObject for data storage but provide nice interface to enduser.

**Methods**
- `edit()`: edit data of object in editor. chosen editor in env var: "EDITOR" will be used

- `_trigger_add`: Triggers are called with (jsconfigs, jsconfig, action)
can register any method you want to respond on some change
- jsconfigs: the obj coming from this class, the collection of jsconfigs = jsxconfig_object
- jsconfig: the jsconfig object
- action: e.g. new, delete, get,stop, ...

- `_triggers_call()`: will go over all triggers and call them with arguments given

- `_data_update()`: will not automatically save the data, don't forget to call self.save()

## JSFactory Class:
### `j.baseclasses.factory`
Is a combination of JSBASE+JSConfigsBCDB class where it combines the features of a factory as well as a config instance if needed. It will include both _CHILDCLASSES and _SCHEMATEXT where the childclasses instances can be generated and the schema text is used to create a config instance for that class itself.  This type of class will show all the objects of the type.

**Methods**
- `get()`: Gets an object from the instance.
- `delete()`: deletes the instance (child object).
- `save()`: save new instance in bcdb with it's configurations.
- `find()`: find all instances(child object) created that satisfy filter options provided. eg: `find(color="red")`

## JSFactoryData Class
### `j.baseclasses.factory_data`
Is a combination of [JSFactory](#jsfactory-class)+[JSConfigBCDB](#jsconfigbcdb-class) class where it combines the features of a factory as well as a config instance if needed. It is similar to [JSFactory](#jsfactory-class) but it can have instances itself.  It acts as a parent, only the children will be shown

**Methods**
Same methods as [JSFactory](#jsfactory-class) and [JSConfigBCDB](#jsconfigbcdb-class)

## ThreebotPackage Class:
### `j.baseclasses.threebot_package`
Is the base class for a package class for a therebot.

**Methods**
- `prepare()`: Called at install time
- `enable()`: enable the use of the package in threebot
- `disable()`: disable the use of the package in threebot when not currently being used
- `start()`: called when threebot starts and the package is loaded
- `stop()`: called when threebot stops
- `install()`: used to install a package to be used in the threebot
- `uninstall()`: called when a package is no longer needed and is to be removed packages loaded in threebot

## BuilderBase Class:
### `j.baseclasses.builder`
Is the base class to create and use a builder.

**Methods**
- `build()`: Build from source code
- `install()`: install and copy required files to be used
- `sandbox()`: Copy all needed config files and bins to be used in creating an flist
- `start()`: start the server/files built and installed
- `stop()`: stop the started server
- `running()`: check if has started and is running
- `clean()`: remove all files resulted from building


## Jumpscale Generated

- To make all short paths jumpscale is generating all its modules and files in `{DIR_BASE}/lib/jumpscale/Jumpscale/*` and fetches it via `{DIR_BASE}/lib/jumpscale/Jumpscale/jumpscale_generated.py`, so actually j.anything comes from this file. If you do new class don't forget to update it via `$ js_init generate`

## See More
**Nested clients**
- Like [TFChain](https://github.com/threefoldtech/jumpscaleX/blob/development_jumpscale/Jumpscale/clients/blockchain/tfchain/TFChainClient.py) client relation with [Wallet](https://github.com/threefoldtech/jumpscaleX/blob/development_jumpscale/Jumpscale/clients/blockchain/tfchain/TFChainWallet.py) client
    - TFChain Factory has a child object class of TFChain Client.
    - Also TFChain Client has a child object of Wallet Factory
    - Finally Wallet Factory has a child object class of Wallet Client.

Explained more in this example from [Jumpscale Tutorials](https://github.com/threefoldtech/jumpscaleX/blob/development_jumpscale/Jumpscale/tutorials/base/tutorials/object_structure/1_object_structure.py)
