// Translation of parse.py to JavaScript, work in progress.

var BASE = 0.75
var HEAD = '<html>\n<svg height=300px width=300px>\n<g transform="translate(150, ' +
     '150), scale({})")>\n'.format(BASE)
var TAIL = "\n</g>\n</svg>\n</html>"

var SPEEDMASTER = [
        {'a_len': 2, 'a_width': 0.5, 'b_off': 2, 'b_len': 23, 
         'c_diameter': 3},
        [
          [1, 
            [12, 'line', ['a_len', 'a_width * 1.5']], 
            [60, 'line', [11, 'a_width']], 
            [240, 'line', ['a_len', 'a_width']]],
          ['a_len + b_off', 
            [12, 'line', ['b_len', 5]]],
          ['b_len - c_diameter', 
            [['1/60', '-1/60'], 'circle', ['c_diameter']]]
        ]
      ]

var SUBMARINER = [
        {'a_len': 3, 'a_width': 0.75, 'b_off': 2, 'b_len': 30, 
        'c_diameter': 3},
        [
          [1,
            [12, 'line', ['a_len', 'a_width * 1.5']],
            [60, 'line', ['a_len', 'a_width']]],
          ['a_len + b_off',
            [1, 'triangle', ['b_len', 'b_len * 0.7']],
            [4, 'line', ['b_len', 'b_len / 3']],
            [12, 'circle', ['b_len * 0.55']]]
        ]
      ]

main()

function main() {
  var out = HEAD
  var watch = SUBMARINER
  var dictionary = watch[0]
  var elements = watch[1]
  elements = replace_matched_items(elements, dictionary)
  var offset = 0
  for (element of elements) {
    offset += element[0]
    out += get_group(offset, element.slice(1))
  }
  print(out+TAIL)
}

function get_group(offset, elements) {
  if (!elements) {
    return
  }
  var out = ""
  var filled_pos = set()
  for (element of elements) {
    var pos = element[0] 
    var shape = element[1] 
    var args = element[2]
    if (isinstance(pos, Number)) {
      pos = get_positions(pos)
    }
    pos = pos.difference(filled_pos)
    filled_pos.update(pos)
    out += get_shapes(pos, shape, args, offset)
  }
  return out
}

function get_positions(n){
  var out = new Set()
  for (i of range(n)) {
    out.add(i/n)
  }
  return out
}

function range(n) {
  return Array.apply(null, Array(5)).map(function (_, i) {return i;});
}

function get_shapes(pos, shape, args, offset) {
  if (shape === 'line') {
    var length = args[0]
    var width = args[1]
    return get_elements(pos, get_line, 
              [100-offset, 100-offset-length, width])
  } else if (shape === 'circle') {
    var diameter = args[0]
    return get_elements(pos, get_circle, [100-offset, diameter])
  } else if (shape === 'triangle') {
    var length = args[0] 
    var width = args[1]
    return get_elements(pos, get_triangle, 
              [100-offset, 100-offset-length, width])
  }
  return ""
}

function get_elements(positions, drawer, args) {
  var out = ""
  for (position of positions) {
    var deg = position * 2*Math.pi - Math.pi/2
    out += drawer([deg] + args)
  }
  return out
}

function get_circle(args) {
  var deg = args[0]
  var ro = args[1]
  var diameter = args [2]
  var cx = Math.cos(deg) * (ro - diameter/2)
  var cy = Math.sin(deg) * (ro - diameter/2)
  return '<circle cx={} cy={} r={} style="stroke-width: 0; fill: rgb(0, 0, ' +
       '0);"></circle>'.format(cx, cy, diameter/2)
}

function get_line(args) {
  var deg = args[0]
  var ri = args[1]
  var ro = args[2]
  var width = args[3]
  var x1 = Math.cos(deg) * ri
  var x2 = Math.cos(deg) * ro
  var y1 = Math.sin(deg) * ri
  var y2 = Math.sin(deg) * ro
  return '<line x1={} y1={} x2={} y2={} style="stroke-width:{}; ' +
       'stroke:#000000"></line>'.format(x1, y1, x2, y2, width)
}

function get_triangle(args) {
  var deg = args[0]
  var ro = args[1]
  var ri = args[2]
  var width = args[3]
  var x1 = (Math.cos(deg) * ro) - (Math.sin(deg) * width / 2)
  var y1 = (Math.sin(deg) * ro) + (Math.cos(deg) * width / 2)
  var x2 = (Math.cos(deg) * ro) + (Math.sin(deg) * width / 2)
  var y2 = (Math.sin(deg) * ro) - (Math.cos(deg) * width / 2)
  var x3 = Math.cos(deg) * ri
  var y3 = Math.sin(deg) * ri
  return '<polygon points="{},{} {},{} {},{}" />'.format(x1, y1, x2, y2, x3, y3)
}

////
///  DICT SUB
//

function replace_matched_items(elements, dictionary) {
  var out = []
  for (element of elements) {
    if (Array.isArray(element)) {
      out.append(replace_matched_items(element, dictionary))
    } else {
      out.append(get_value_of_exp(element, dictionary))
    }
  }
  return out
}

function get_value_of_exp(exp, dictionary) {
  if (isNumeric(exp)) {
    return exp
  }
  for (var key in dictionary) {
    if (dictionary.hasOwnProperty(key)) {
      var value = dictionary[key]
      exp = exp.replace(key, str(value))
    }
  }
  if (re.search('[a-zA-Z]', exp)) {
    return exp
  }
  return eval_expr(exp)
}

function isNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

////
///  EVAL
//

var operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
       ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
       ast.USub: op.neg}

function eval_expr(expr) {
  return eval_(ast.parse(expr, mode='eval').body)
}

function eval_(node) {
  if (isinstance(node, ast.Num)) {
    return node.n
  } else if (isinstance(node, ast.BinOp)) {
    return operators[type(node.op)](eval_(node.left), eval_(node.right))
  } else if (isinstance(node, ast.UnaryOp)) {
    return operators[type(node.op)](eval_(node.operand))
  } else {
    raise TypeError(node)
  }
}

