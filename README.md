Watch Face Description Language
===============================
**Language for defining watch face design.**

[Watches](doc/watches.png)

### Output
[Speedmaster](doc/speedmaster.png)

### Input
```python
[
  {"a_len": 2, "a_width": 0.5, "b_off": 2, "b_len": 23, 
   "c_diameter": 3},
  [
    [1, 
      [12, "line", ["a_len", "a_width * 1.5"]], 
      [60, "line", [11, "a_width"]], 
      [240, "line", ["a_len", "a_width"]]],
    ["a_len + b_off", 
      [12, "line", ["b_len", 5]]],
    ["b_len - c_diameter", 
      [{"1/60", "-1/60"}, "circle", ["c_diameter"]]]
  ]
]
```

### How to run
```bash
$ git clone ...
$ cd wdl
$ ./parse speedmaster.txt
```
* Open 'index.html'.

### Description
Watch is defined with following Python data structures: List, Dictionary and Set.
On top level is a list that contains two elements. First one is a dictionary of variables, that defines name, value pairs. 
```python
  {"a_len": 2, "a_width": 0.5, "b_off": 2, "b_len": 23, 
   "c_diameter": 3},
```

Second element of the top level list is a list that contains the descriptions of watche's face elements. 
```python
  [
    [1, 
      [12, "line", ["a_len", "a_width * 1.5"]], 
      [60, "line", [11, "a_width"]], 
      [240, "line", ["a_len", "a_width"]]],
    ["a_len + b_off", 
      [12, "line", ["b_len", 5]]],
    ["b_len - c_diameter", 
      [{"1/60", "-1/60"}, "circle", ["c_diameter"]]]
  ]
``` 
Elements are grouped by distance from the watches edge.  0 means on the edge and 100 in the center of the watch. First element of the list denotes how much toward the center are all the elements in the group positioned. In this case only one houndreth of the watches diameter.
```python
    [1, 
      [12, "line", ["a_len", "a_width * 1.5"]], 
      [60, "line", [11, "a_width"]], 
      [240, "line", ["a_len", "a_width"]]],
```
This group then contains list of elements, that are repeated around the face. For instance the first list  draws 12 lines of length 'a_len' and width 'a_width * 1.5'.
```python
      [12, "line", ["a_len", "a_width * 1.5"]], 
```

### Simple Example
```python
[
  {"line_len": 20, "line_width": 3},
  [
    [0, 
      [12, "line", ["line_len", "line_width"]]]
  ]
]
```
[simple example](doc/example.png)


