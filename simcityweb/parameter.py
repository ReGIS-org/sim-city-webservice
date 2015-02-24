from util import abort, make_hash

def parse_parameters(parameters, parameter_specs):
    paramset = frozenset(parameters)
    param_specset = frozenset([param['name'] for param in parameter_specs])
    
    if not (paramset <= param_specset):
        abort(400, "parameters " + str(list(paramset - param_specset)) + " not specified (" + str(parameters) + " vs spec " + str(parameter_specs))
    
    params = {}
    for spec_raw in parameter_specs:
        spec = parse_parameter_spec(spec_raw)
        try:
            value = parameters[spec.name]
            del parameters[spec.name]
            value = spec.coerce(value)
        except KeyError:
            params[spec.name] = spec.default
        except (TypeError, ValueError):
            abort(400, "value of " + str(value) + " for parameter does not comply to " + str(spec.dtype))
        else:
            if spec.is_valid(value):
                params[spec.name] = value
            else:
                abort(400, "value of " + str(value) + " for parameter does not comply to " + str(spec))
    return params

def parse_parameter_spec(idict):        
    default = idict.get('default', None)
    if idict['type'] == 'interval':
        dtype = idict.get('dtype', 'float')
        return IntervalSpec(idict['name'], idict['min'], idict['max'], default, dtype)
    if idict['type'] == 'choice':
        dtype = idict.get('dtype', 'str')
        return ChoiceSpec(idict['name'], idict['choices'], default, dtype)
        
    raise ValueError('parameter type not recognized')

class ParameterSpec(object):
    TYPE_STR = {
        'int': int,
        'float': float,
        'str': str
    }
    def __init__(self, name, default, dtype):
        if type(dtype) == type:
            self._dtype = dtype
        else:
            try:
                self._dtype = ParameterSpec.TYPE_STR[dtype]
            except KeyError:
                raise ValueError("Type " + str(dtype) + " unknown; use one of " + str(ParameterSpec.keys()))
        
        if default is None:
            self._default = None
        else:
            self._default = self.coerce(default)
        self._name = name
    
    @property
    def default(self):
        return self._default
    @property
    def dtype(self):
        return self._dtype
    @property
    def name(self):
        return self._name
        
    def coerce(self, value):
        if type(value) == self.dtype:
            return value
        else:
            return self.dtype(value)
    
    def is_valid(self, value):
        raise NotImplementedError

class ChoiceSpec(ParameterSpec):
    def __init__(self, name, choices, default, dtype):
        if type(choices) != list:
            raise ValueError("Choices must be provided as a list")
        if len(choices) == 0:
            raise ValueError("At least one choice is required.")
        if default is None:
            default = choices[0]
        
        super(ChoiceSpec, self).__init__(name, default, dtype)
        self._choices = [self.coerce(choice) for choice in choices]
        self._choices.sort()
    
    @property
    def choices(self):
        return self._choices.copy()
    
    def is_valid(self, value):
        return type(value) == self.dtype and value in self._choices
    
    def __str__(self):
        return self.name + ': choice ' + str(self._choices) + ' ' + str(self.dtype)
        
    def __eq__(self, other):
        return type(self) == type(other) and self._choices == other._choices and self.default == other.default and self.dtype == other.dtype
    
    def __hash__(self):
        return make_hash(self._default, self.dtype, *self._choices)
        
class IntervalSpec(ParameterSpec):
    def __init__(self, name, min, max, default, dtype):
        if default is None:
            default = (self._min + self._max) / 2
        super(IntervalSpec, self).__init__(name, default, dtype)
        
        self._min = self.coerce(min)
        self._max = self.coerce(max)

        if self._min > self._max:
            raise ValueError("Minimum to an interval must be smaller than maximum")
        
        if not self.is_valid(self.default):
            raise ValueError("default value for interval not valid")
        
    @property
    def max(self):
        return self._max
    @property
    def min(self):
        return self._min
    
    def is_valid(self, value):
        return value >= self.min and value <= self.max and type(value) == self.dtype

    def __str__(self):
        return self.name + ': interval [' + str(self.min) + ',' + str(self.max) + '] ' + str(self.dtype)
        
    def __eq__(self, other):
        return type(self) == type(other) and self._min == other._min and self._max == other._max and self._default == other._default and self.dtype == other.dtype
    
    def __hash__(self):
        return make_hash(self._min, self._max, self._default, self.dtype)
