# SIM-CITY webservice
#
# Copyright 2015 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

try:
    input = raw_input
except NameError:
    pass

_input_mechanism = input


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
    response = _input_mechanism('{0} [{1}]? '
                          .format(message, default_message)).lower()
    while response not in possible_answers:
        response = _input_mechanism('Please answer yes or no. {0} [{1}]? '
                             .format(message, default_message)).lower()

    return response in truthy


def dialog(message, default_response=None):
    ''' Provide a command-line dialog for the user. '''
    if default_response is None:
        response = _input_mechanism('{0}: '.format(message))
        while response == '':
            response = _input_mechanism("Value '{0}' invalid. {1}: "
                                        .format(response, message))
    else:
        response = _input_mechanism('{} [{}]: '
                                    .format(message, default_response))
        if response == '':
            response = default_response

    return response


def choice_dialog(message, options, default_response=None):
    ''' Provide a command-line dialog with fixed options for the user. '''
    if len(options) == 0:
        raise ValueError("Cannot choose from empty options")
    elif len(options) == 1:
        return next(iter(options))

    message = '{0} ({1})'.format(message, str(list(options))[1:-1])

    options = set(options)
    if default_response is None:
        response = _input_mechanism('{0}: '.format(message))
        while response not in options:
            response = _input_mechanism("Value '{0}' invalid. {1}: "
                                        .format(response, message))
    else:
        if default_response not in options:
            raise ValueError(
                "Default response '{0}' is not part of options {1}"
                .format(default_response, str(list(options))[1:-1]))
        options.add('')

        response = _input_mechanism('{} [{}]: '
                                    .format(message, default_response))

        while response not in options:
            response = _input_mechanism("Value '{0}' invalid. {1} [{2}]: "
                                        .format(response, message,
                                                default_response))

        if response == '':
            response = default_response

    return response


def new_or_overwrite(path, message=None, default_response=False):
    ''' Either given file does not exist, or the user has to confirm whether
        to overwrite it. '''
    directory, filename = os.path.split(path)
    if message is None:
        message = "{0} exists, overwrite".format(filename)
    return (not os.path.exists(path) or
            confirm(message, default_response=default_response))
