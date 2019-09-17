import re
import os
from utils import pull_from_context



def eval_expressions_block(expressions, context):
    for expr in expressions:
        expr.eval(context)

        if context.get('_ret') is not None:
            return context['_ret']

        if context.get('_obj') is not None:
            return Object(context)


class Nothing:
    def eval(self, context):
        return self


class Import:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def eval(self, context):
        parse_func = pull_from_context(context, '__parse')
        source_filedir = pull_from_context(context, '__filedir')
        source_path = os.path.join(source_filedir, self.path + '.mitoy')

        with open(source_path) as fh:
            module = parse_func(fh.read(), source_path)

            return Object(module.context, self.name)


class ValueString:
    def __init__(self, value):
        self.value = value

    def eval(self, context):
        return re.sub(r'(?<!\\)\\n', '\n', self.value[1:-1])


class ValueFloat:
    def __init__(self, value):
        self.value = value

    def eval(self, context):
        return float(self.value)


class ValueInt:
    def __init__(self, value):
        self.value = value

    def eval(self, context):
        return int(self.value)


class Module:
    def __init__(self, topdefs):
        self.topdefs = topdefs
        self.context = {}

    def eval(self, context):
        self.context.update(context)

        for topdef in self.topdefs:
            self.context[topdef.name] = topdef.eval(self.context)

        return self

    def run(self, name, *args):
        return FunctionCall(Memory(name), args).eval({'_pc': self.context})


class Object:
    def __init__(self, content, name="<obj>"):
        self.name = name
        self.content = content

    def eval(self, context={}):
        return self


class Field:
    def __init__(self, obj, field):
        self.obj = obj
        self.field = field

    def eval_content(self, context):
        if isinstance(self.obj, (Field, FunctionCall)):
            obj = self.obj.eval(context)
        else:
            obj = Memory(self.obj).eval(context)

        return obj.eval(context).content

    def eval(self, context):
        if isinstance(self.obj, (Field, FunctionCall)):
            obj = self.obj.eval(context)
        else:
            obj = Memory(self.obj).eval(context)

        return obj.eval(context).content[self.field]


class Assign:
    def __init__(self, name, value, overwrite=False):
        self.name = name
        self.value = value
        self.overwrite = overwrite

    def eval(self, context):
        if isinstance(self.name, Field):
            content = self.name.eval_content(context)

            mem = Memory(
                self.name.field,
                self.value.eval(context),
                read=False,
                overwrite=self.overwrite
            )

            return mem.eval(content)

        else:
            mem = Memory(
                self.name,
                self.value.eval(context),
                read=False,
                overwrite=self.overwrite
            )

            return mem.eval(context)


class Memory:
    def __init__(self, name, value=None, read=True, overwrite=False):
        self.name = name
        self.value = value
        self.read = read
        self.overwrite = overwrite

    def eval(self, context):
        if self.read:
            ctx = context

            while ctx is not None:
                if self.name in ctx:
                    return ctx[self.name]
                ctx = ctx.get('_pc')

            raise KeyError(self.name)
        else:
            if self.name.startswith('_'):
                context[self.name] = self.value
                return

            ctx = context

            while ctx is not None:
                if self.name in ctx:
                    if ctx is not context and not self.overwrite:
                        raise ValueError('Can not shadow other variables')

                    ctx[self.name] = self.value
                    return
                ctx = ctx.get('_pc')

            context[self.name] = self.value


class Function:
    def __init__(self, name, args, body, context=None):
        self.name = name
        self.args = args
        self.body = body
        self.context = context

    def eval(self, context):
        func = Function(self.name, self.args, self.body, context)

        context[self.name] = func

        return func


class FunctionCall:
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

    def eval(self, outer_context):
        if isinstance(self.function, Function):
            function = self.function
        else:
            function = self.function.eval(outer_context)

        context = {'_pc': function.context}

        if len(function.args) != len(self.arguments):
            raise Exception(
                f'Unexpected amount of arguments ({len(function.args)}'
                f' -> {len(self.arguments)}) in `{self.function.name}`'
            )

        for arg_name, arg_value in zip(function.args, self.arguments):
            context[arg_name] = arg_value.eval(outer_context)

        if callable(function.body):
            return function.body(context)

        return eval_expressions_block(function.body, context)


class IfStatement:
    def __init__(self, cond, true, false):
        self.cond = cond
        self.true = true
        self.false = false

    def eval(self, context):
        val = None

        if self.cond.eval(context):
            val = eval_expressions_block(self.true or [], context)
        else:
            val = eval_expressions_block(self.false or [], context)

        return val


class ForLoop:
    def __init__(self, init, cond, tick, body):
        self.init = init
        self.cond = cond
        self.tick = tick
        self.body = body

    def eval(self, context):
        self.init.eval(context)

        while self.cond.eval(context):
            eval_expressions_block(self.body, context)

            if context.get('_ret') is not None:
                return context['_ret']

            if context.get('_obj') is not None:
                return Object(context)

            self.tick.eval(context)


class UnaryOp:
    def __init__(self, value, operation):
        self.value = value
        self.operation = operation

    def eval(self, context):
        op = self.operation
        value = self.value.eval(context)

        if op == "'~'":
            return ~ value
        if op == "'!'":
            return not value
        if op == "'-'":
            return - value

        raise ValueError(f'Unknown operation: {op}')


class BinaryOp:
    def __init__(self, left, right, operation):
        self.left = left
        self.right = right
        self.operation = operation

    def eval(self, context):
        op = self.operation
        l = self.left.eval(context)
        r = self.right.eval(context)

        if op == "'+'":
            return l + r
        if op == "'-'":
            return l - r
        if op == "'/'":
            return l / r
        if op == "'//'":
            return l // r
        if op == "'*'":
            return l * r
        if op == "'%'":
            return l % r
        if op == "'>'":
            return l > r
        if op == "'>='":
            return l >= r
        if op == "'<'":
            return l < r
        if op == "'<='":
            return l <= r
        if op == "'=='":
            return l == r
        if op == "'!='":
            return l != r
        if op == "'&&'":
            return l and r
        if op == "'||'":
            return l or r
        if op == "'&'":
            return l & r
        if op == "'|'":
            return l | r
        if op == "'^'":
            return l ^ r
        if op == "'>>'":
            return l >> r
        if op == "'<<'":
            return l << r

        raise ValueError(f'Unknown operation: {op}')
