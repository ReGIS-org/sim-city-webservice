import os


def confirm(message, default_response=True):
    ''' Provide a command-line yes-no question for the user. '''
    truthy = ['y', 'yes']
    falsy = ['n', 'no']
    if default_response:
        truthy.append('')
        default_message = 'Y/n'
    else:
        falsy.append('')
        default_message = 'y/N'

    possible_answers = truthy + falsy
    response = raw_input('{} [{}]? '.format(message, default_message)).lower()
    while response not in possible_answers:
        response = raw_input('Please answer yes or no. {} [{}]? '
                             .format(message, default_message)).lower()

    return response in truthy


def dialog(message, default_response=None, options=None):
    ''' Provide a command-line dialog for the user. '''
    if options is not None:
        if len(options) == 0:
            raise ValueError("Cannot choose from empty options")
        elif len(options) == 1:
            return options[0]
        message = '{} ({})'.format(message, str(options)[1:-1])

    if default_response is None:
        response = raw_input('{}: '.format(message))
        while ((options is not None and response not in options) or
               (options is None and response == '')):
            response = raw_input("Value '{}' invalid. {}: "
                                 .format(response, message))
    else:
        response = raw_input('{} [{}]: '.format(message, default_response))
        while options is not None and response not in [''] + options:
            response = raw_input("Value '{}' invalid. {} [{}]: "
                                 .format(response, message, default_response))

        if response == '':
            response = default_response

    return response


def new_or_overwrite(path, message=None):
    ''' Either given file does not exist, or the user has to confirm whether
        to overwrite it. '''
    directory, file = os.path.split(path)
    if message is None:
        message = "{} exists, overwrite".format(file)
    return (not os.path.exists(path) or
            confirm(message, default_response=False))
