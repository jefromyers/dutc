from datetime import date


class ExpiredFunctionException(Exception):
    def __init__(self, message):            
        super().__init__(message)
            
# This feels way too busy. Maybe it would be better to make each modality a
# decorator?
def notify(msg, by=None, enforce=False):
    def dec(f):
        def wrapper(*args, **kwargs):
            if by:
                print(f"{f.__name__}() WARNING: {msg} {by:%m/%d/%Y}")
                if enforce and date.today() >= by:
                    raise ExpiredFunctionException(f"Must fix")
            else:
                print(f"{f.__name__}() WARNING: {msg}")
            r = f(*args, **kwargs)
            return r

        return wrapper

    return dec
