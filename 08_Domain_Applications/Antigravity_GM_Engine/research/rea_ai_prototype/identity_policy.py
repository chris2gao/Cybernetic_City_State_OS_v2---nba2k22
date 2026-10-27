"""Separate read feasibility from identity qualification for effectful actions."""
from dataclasses import dataclass

@dataclass(frozen=True)
class IdentityHypothesis:
 mapped_readable:bool
 requested_bytes:int
 inside_staff_pool:bool|None
 aligned_to_staff_stride:bool|None
 reciprocal_owner_match:bool|None
 stable_logical_identity:bool=False

 def may_read_bounded_projection(self,budget=65536):
  # Pool membership and alignment are observations, never read permissions.
  return self.mapped_readable is True and type(self.requested_bytes) is int and 0<self.requested_bytes<=budget

 def qualified_for_write_or_native_call(self):
  # This conservative prototype has no alternate allocation proof installed.
  return self.may_read_bounded_projection() and all(x is True for x in (self.inside_staff_pool,self.aligned_to_staff_stride,self.reciprocal_owner_match,self.stable_logical_identity))
