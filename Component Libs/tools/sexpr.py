"""Small lossless-atom S-expression reader/writer for library maintenance."""
import re

class Quoted(str):
    pass

def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack, root = [], None
    for token in tokens:
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            else:
                assert root is None
                root = node
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            value = Quoted(token[1:-1]) if token.startswith('"') else token
            stack[-1].append(value)
    assert not stack
    return root

def dump(node, level=0):
    if not isinstance(node, list):
        return '"' + node + '"' if isinstance(node, Quoted) else str(node)
    if not any(isinstance(x, list) for x in node):
        return '(' + ' '.join(dump(x) for x in node) + ')'
    parts = []
    for item in node:
        parts.append(('\n' + '  ' * (level + 1) if isinstance(item, list) else (' ' if parts else '')) + dump(item, level + 1))
    return '(' + ''.join(parts) + ')'

def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]

def child(node, key):
    return next(iter(children(node, key)), None)

def walk(node):
    if isinstance(node, list):
        yield node
        for item in node:
            yield from walk(item)
