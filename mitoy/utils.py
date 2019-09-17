def pull_from_context(ctx, name):
    while ctx is not None:
        if name in ctx:
            return ctx[name]

        ctx = ctx.get('_pc')
