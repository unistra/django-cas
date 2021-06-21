def cas_callbacks(response_data, callbacks):
    for path in callbacks:
        i = path.rfind('.')
        module, callback = path[:i], path[i+1:]
        try:
            mod = __import__(module, fromlist=[''])
        except ImportError as e:
            print("Import Error: %s" % e)
        try:
            func = getattr(mod, callback)
        except AttributeError as e:
            print("Attribute Error: %s" % e)
        return func(response_data)
