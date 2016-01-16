from Expr import Expr

class Table:
  def __init__(self):
    self._contents = {}
    self._defined_functions = {}
    self._scopes = [{ '_variables' : {} , '_functions' : {}}]

  """Create NEW scope nested inside the last one"""
  def create_new_scope(self):
    self._scopes.append({ '_variables' : {} , '_functions' : {}})

  """Destroy the INNERMOST scope"""
  def destroy_current_scope(self):
    self._scopes.pop()

  """Check whether the variable exists in any scope"""
  def contains(self, variable_name):
    for scope in reversed(self._scopes):
      if variable_name in scope['_variables']:
        return True
    return False

  """Get the variable with the specified name"""
  def get_var(self, variable_name):
    for scope in reversed(self._scopes):
      if variable_name in scope['_variables']:
        return scope['_variables'][variable_name]

  """OBSOLETE: Get boolean value represending whether the variable is lexpr"""
  def get_lexpr(self, variable_name):
    for scope in reversed(self._scopes):
      if variable_name in scope['_variables']:
        return scope['_variables'][variable_name].is_lexpr

  """OBSOLETE: Get the type of the variable"""
  def get_type(self, variable_name):
    for scope in reversed(self._scopes):
      if variable_name in scope['_variables']:
        return scope['_variables'][variable_name]._type

  """Declare a variable in current scope"""
  def declare_var(self, variable_name, var_type):
    self._scopes[-1]['_variables'][variable_name] = var_type.set_to_lexpr()

  """Declare a function in current scope"""
  def declare_fun(self, function_name, _fun_from, _fun_to):
    self._scopes[-1]['_functions'][function_name] = \
      Expr("FUNCTION", is_function = True, fun_from = _fun_from, fun_to = _fun_to)

  """Define a function in the global scope"""
  def define(self, function_name, _fun_from, _fun_to):
    self._defined_functions[function_name] = \
      Expr("FUNCTION", is_function = True, fun_from = _fun_from, fun_to = _fun_to)

  """Returns a boolean represending whether the function is declared in any scope"""
  def is_declared(self, function_name, fun_from, fun_to):
    for scope in reversed(self._scopes):
      if function_name in scope['_functions']:
        function = scope['_functions'][function_name]
        return function._function_from_types == fun_from \
            and function._function_to_types == fun_to
    return False

  """Returns a boolean represending whether the function is defined in the global scope"""
  def is_defined(self, function_name, fun_from, fun_to):
    if not function_name in self._defined_functions:
      return False
    else:
      function = self._defined_functions[function_name]
      return function._function_from_types == fun_from \
          and function._function_to_types == fun_to

  """Returns a boolean represending whether the function is defined
  "" in the global scope without checking its parameters and return type"""
  def is_JUST_declared(self, function_name):
    for scope in reversed(self._scopes):
      if function_name in scope['_functions']:
        return True
    return False

  """Returns the function with the specified type"""
  def get_function(self, function_name):
    for scope in reversed(self._scopes):
      if function_name in scope['_functions']:
        return scope['_functions'][function_name]
    raise Exception("Should check whether the function exists first!")

  """Return a boolean represending whether the function parameters
  "" are of the specified type """
  def is_function_from(self, function_name, etype):
    return self.get_function(function_name)._function_from_types == etype


  """Return a boolean represending whether the function return type
  "" is of the specified type """
  def is_function_to(self, function_name, etype):
    return self.get_function(function_name)._function_to_types == etype