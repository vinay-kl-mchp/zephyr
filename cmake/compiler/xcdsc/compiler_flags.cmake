# SPDX-FileCopyrightText: Copyright (c) 2026 Microchip Technology Inc.
# SPDX-License-Identifier: Apache-2.0

include(${ZEPHYR_BASE}/cmake/compiler/gcc/compiler_flags.cmake)

# Start from the GCC baseline above and override only XC-DSC-specific
# behavior.

########################################################
# This section covers flags related to optimization.  #
########################################################
set_compiler_property(PROPERTY optimization_debug -O1)
set_compiler_property(PROPERTY optimization_speed -O3)
set_compiler_property(PROPERTY optimization_size -O2)
set_compiler_property(PROPERTY optimization_size_aggressive -Os)

# XC-DSC's narrower warning set.
check_set_compiler_property(PROPERTY warning_base
  -Wall
  -Wformat
  -Wformat-security
  -Wno-format-zero-length
  -Wno-unused-but-set-variable
)

# Linker script flag.
set_compiler_property(PROPERTY linker_script -Wl,-T)

# Additional compiler flags for dspic (XC-DSC-specific flags).
# Save intermediate files (optional, helpful for inspection)
set_compiler_property(PROPERTY save_temps -save-temps=obj)
# Smart I/O conversion for format strings (safe printf optimizations)
list(APPEND TOOLCHAIN_C_FLAGS -msmart-io=1)
# Disable SFR access warnings
list(APPEND TOOLCHAIN_C_FLAGS -msfr-warn=off)
# Disable instruction scheduling (for stability)
list(APPEND TOOLCHAIN_C_FLAGS -fno-schedule-insns -fno-schedule-insns2)
list(APPEND TOOLCHAIN_C_FLAGS -fno-omit-frame-pointer)
