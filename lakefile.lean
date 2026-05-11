import Lake
open Lake DSL

package «omega_core» where
  -- add package configuration options here

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.29.1"

@[default_target]
lean_lib «OmegaCore» where
  -- add library configuration options here
