# Node System Module

The node system module is an interface allowing you to manipulate nodes on a canvas 
to assemble a logic that can allow you to describe how to patch a file, a text,
an image, etc.

## Node sub-module

The directory `node` contains a directory for every type of nodes, plus a `base` 
directory for special functions and class used by the other type of nodes.

These type of nodes are:
- `decimal`: a node that can be used to manipulate decimal values (`double` in C++).
- `variant`: a node that can be used to contains any type of value. Useful to
  use a function that can use any type of value (example : a print-like function).

All the directories contains some special files : 
- `register` file to register all the nodes in the registry.
- `data` file containing the implementation of the type itself.
