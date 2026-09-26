# SPDX-FileCopyrightText: Copyright (c) 2026 Microchip Technology Inc.
# SPDX-License-Identifier: Apache-2.0

if(CONFIG_BIG_ENDIAN)
  set_property(GLOBAL PROPERTY PROPERTY_OUTPUT_FORMAT elf32-big)
else()
  set_property(GLOBAL PROPERTY PROPERTY_OUTPUT_FORMAT elf32-little)
endif()
zephyr_include_directories(${DFP_ROOT}/xc16/support/generic/h/)
zephyr_include_directories(${DFP_ROOT}/xc16/support/dsPIC33A/h/)
zephyr_include_directories(${XCDSC_TOOLCHAIN_PATH}/support/generic/h/)
zephyr_include_directories(include)
add_subdirectory(core)
