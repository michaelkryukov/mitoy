import asts
from utils import pull_from_context


builtins = {}


# ----------------------------------------------------------------------------


def add_function(name, args, func, pass_context=False):
    def wrapper(ctx):
        func_args = []

        for arg in args:
            func_args.append(ctx[arg])

        if pass_context:
            return func(*func_args, ctx=ctx)
        else:
            return func(*func_args)

    builtins[name] = asts.Function(name, args, wrapper)


def get_builtins():
    return builtins


# ----------------------------------------------------------------------------


def write_to_file(filename, content):
    with open(filename, 'w') as fh:
        fh.write(content)


def throw(reason):
    raise Exception(reason)


def make_array_object(source_array=()):
    array = [*source_array]

    def _add(v):
        return array.append(v)

    def _get(i):
        return array[i]

    def _set(i, v):
        array[i] = v

    def _len():
        return len(array)

    def _cpy():
        return make_array_object(array)

    return asts.Object({
        'add': asts.Function('add', ['v'], lambda ctx: _add(ctx['v'])),
        'get': asts.Function('get', ['i'], lambda ctx: _get(ctx['i'])),
        'set': asts.Function('set', ['i', 'v'], lambda ctx: _set(ctx['i'], ctx['v'])),
        'len': asts.Function('len', [], lambda ctx: _len()),
        'cpy': asts.Function('cpy', [], lambda ctx: _cpy()),
    })


# ----------------------------------------------------------------------------


add_function('MakeList', [], make_array_object)
add_function('Throw', ['reason'], throw)

add_function('Str', ['val'], str)
add_function('Int', ['val'], int)
add_function('Float', ['val'], float)

add_function('StrSlice', ['val', 's', 'e'], lambda val, s, e: val[s: e])
add_function('StrLen', ['val'], lambda val: len(val))

add_function('Input', [], lambda: input())
add_function('WriteToFile', ['filename', 'content'], write_to_file)

add_function('TraceNl', ['val'], print)
add_function('Trace', ['val'], lambda val: print(val, end=""))
