# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

from pants.base.exceptions import TargetDefinitionException
from pants.base.payload import Payload
from pants.base.payload_field import PrimitiveField
from pants.build_graph.target import Target


class PrepCommand(Target):
  """A shell command to be run prior to running a goal.

  For example, you can use `prep_command()` to execute a script that sets up tunnels to database
  servers. These tunnels could then be leveraged by integration tests.

  Pants will only execute the `prep_command()` under the specified goal, when processing targets
  that depend on the `prep_command()` target.  If not otherwise specified, prep_commands
  execute in the test goal.

  See also jvm_prep_command for running tasks defined by a JVM language.

  :API: public
  """
  _goals=frozenset()

  @staticmethod
  def add_goal(goal):
    """Add a named goal to the list of valid goals for the 'goal' parameter."""
    PrepCommand._goals = frozenset(list(PrepCommand._goals) + [goal])

  @classmethod
  def reset(cls):
    """Used for testing purposes to reset state."""
    cls._goals=frozenset()

  @staticmethod
  def goals():
    return PrepCommand._goals

  def __init__(self, prep_executable=None, prep_args=None, payload=None, prep_environ=False,
               goal=None, **kwargs):
    """
    :API: public

    :param prep_executable: The path to the executable that should be run.
    :param prep_args: A list of command-line args to the excutable.
    :param prep_environ: If True, the output of the command will be treated as
      a \\\\0-separated list of key=value pairs to insert into the environment.
      Note that this will pollute the environment for all future tests, so
      avoid it if at all possible.
    :param goal: Pants goal to run this command in [test, binary or compile]. If not specified,
                 runs in the 'test' goal.
    """
    payload = payload or Payload()
    goal = goal or 'test'

    payload.add_fields({
      'goal': PrimitiveField(goal),
      'prep_command_executable': PrimitiveField(prep_executable),
      'prep_command_args': PrimitiveField(prep_args or []),
      'prep_environ': PrimitiveField(prep_environ),
    })
    super(PrepCommand, self).__init__(payload=payload, **kwargs)
    if not prep_executable:
      raise TargetDefinitionException(self, 'prep_executable must be specified.')
    if goal not in self.goals():
      raise TargetDefinitionException(self, 'Got goal "{}". Goal must be one of {}.'.format(
          goal, self.goals()))
