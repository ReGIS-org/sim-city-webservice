from util import abort, make_hash

def parse_parameters(parameters, parameter_specs):
    paramset = frozenset(parameters)
    param_specset = frozenset(parameter_specs)
    
    if not (paramset <= param_specset):
        abort(400, "parameters " + str(list(paramset - param_specset)) + " not specified")
    
    params = {}
    for name, spec_raw in parameter_specs.items():
        spec = parse_parameter_spec(spec_raw)
        try:
            value = parameters[name]
            del parameters[name]
            value = spec.coerce(value)
        except KeyError:
            params[name] = spec.default
        except (TypeError, ValueError):
            abort(400, "value of " + str(value) + " for parameter " + name + " does not comply to " + str(spec.dtype))
        else:
            if spec.is_valid(value):
                params[name] = value
            else:
                abort(400, "value of " + str(value) + " for parameter " + name + " does not comply to " + str(spec))
    return params


TYPE_STR = {
    'int': int,
    'float': float,
    'str': str
}

def extract_and_convert(value, type_str):
    try:
        return TYPE_STR[type_str](value)
    except KeyError:
        raise ValueError("Type '" + type_str + "' unknown")

def parse_parameter_spec(idict):
    if idict['type'] == 'interval':
        try:
            dtype = idict['dtype']
        except:
            dtype = 'float'
        min = extract_and_convert(idict['min'], dtype)
        max = extract_and_convert(idict['max'], dtype)
        try:
            default = extract_and_convert(idict['default'], dtype)
        except:
            default = None
        return Interval(min, max, default)
        
    raise ValueError('parameter type not recognized')

class ParameterSpec(object):
    def __init__(self, default):
        self._default = default
    
    @property
    def default(self):
        return self._default
    @property
    def dtype(self):
        return type(self.default)
        
    def coerce(self, value):
        if type(value) == self.dtype:
            return value
        else:
            return self.dtype(value)
    
    def is_valid(self, value):
        raise NotImplementedError

class Interval(ParameterSpec):
    def __init__(self, min, max, default):
        if default is None:
            default = (self._min + self._max) / 2
        super(Interval, self).__init__(default)
        
        if type(min) != self.dtype:
            raise ValueError("Type of minimum not compatible with " + str(self.dtype))
        if type(max) != self.dtype:
            raise ValueError("Type of maximum not compatible with " + str(self.dtype))
        if min > max:
            raise ValueError("Minimum to an interval must be smaller than maximum")
            
        self._min = min
        self._max = max

        if not self.is_valid(self.default):
            raise ValueError("default value for interval not valid")
        
    @property
    def max(self):
        return self._max
    @property
    def min(self):
        return self._min
    @property
    def default(self):
        return self._default
    
    def is_valid(self, value):
        return value >= self.min and value <= self.max and type(value) == self.dtype

    def __str__(self):
        return 'interval [' + str(self.min) + ',' + str(self.max) + '] ' + str(self.dtype)
        
    def __eq__(self, other):
        return type(self) == type(other) and self.min == other.min and self.max == other.max and self.dtype == other.dtype
    
    def __hash__(self):
        return make_hash(self._min, self._max, self.dtype)