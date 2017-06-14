from gifi.command import CommandException


def ask(question, value):
    raw_value = raw_input("%s (%s): " % (question, value))
    if raw_value is not '':
        value = parse_value(raw_value, type(value))
    return value


def parse_value(rawValue, destType):
    rawValue = str(rawValue)
    if destType is bool:
        if rawValue in ['True', 'true', 'yes', '1']:
            return True
        elif rawValue in ['False', 'false', 'no', '0']:
            return False
        else:
            raise CommandException("Wrong value '%s' (with: %s) for '%s'" % (rawValue, type(rawValue), destType))
    elif destType is str:
        return rawValue
    elif destType is unicode:
        return rawValue
    elif destType is int:
        return int(rawValue)
    else:
        raise CommandException('Unsupported type: %s' % destType)
