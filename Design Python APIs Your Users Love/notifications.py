def notify(msg, by=None):
    def dec(f):
        def wrapper(*args, **kwargs):
            if by:
                print(f"{f.__name__}() WARNING: {msg} {by:%m/%d/%Y}")
            else:
                print(f"{f.__name__}() WARNING: {msg}")
            r = f(*args, **kwargs)
            return r

        return wrapper

    return dec
