/*
 * SPDX-FileCopyrightText: Copyright (c) 2026 Microchip Technology Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/toolchain.h>

#include <xc.h>

LOG_MODULE_REGISTER(dspic, 4);

static volatile uint32_t reason, address;

#define EXCEPTION_HANDLER __attribute__((interrupt, no_auto_psv, weak, naked))
#define BUS_ERROR_MASK    0xF
#define MATH_ERROR_MASK   0x1F
#define STACK_ERROR_MASK   0x10
#define GENERAL_TRAP_MASK 0x8000000Fu

void EXCEPTION_HANDLER _BusErrorTrap(void);
void EXCEPTION_HANDLER _AddressErrorTrap(void);
void EXCEPTION_HANDLER _IllegalInstructionTrap(void);
void EXCEPTION_HANDLER _MathErrorTrap(void);
void EXCEPTION_HANDLER _StackErrorTrap(void);
void EXCEPTION_HANDLER _GeneralTrap(void);
void EXCEPTION_HANDLER _ReservedTrap0(void);
void EXCEPTION_HANDLER _ReservedTrap7(void);

void EXCEPTION_HANDLER _ReservedTrap0(void)
{
}
void EXCEPTION_HANDLER _ReservedTrap7(void)
{
}

/* Bus error */
void EXCEPTION_HANDLER _BusErrorTrap(void)
{
	reason = INTCON3 & BUS_ERROR_MASK;
	address = PCTRAP;
	LOG_ERR("ERROR !!! Exception reason = %d, address = 0x%x\n", reason, address);
	INTCON3 &= ~(BUS_ERROR_MASK);
	PCTRAP = 0;
	k_fatal_halt(K_ERR_CPU_EXCEPTION);
}

/* Address error */
void EXCEPTION_HANDLER _AddressErrorTrap(void)
{
	address = PCTRAP;
	LOG_ERR("ERROR !!! Exception reason = %s, address = 0x%x\n", "Address Error", address);
	INTCON1bits.ADDRERR = 0;
	PCTRAP = 0;
	k_fatal_halt(K_ERR_CPU_EXCEPTION);
}

/* Illegal instruction */
void EXCEPTION_HANDLER _IllegalInstructionTrap(void)
{
	address = PCTRAP;
	LOG_ERR("ERROR !!! Exception reason = %s, address = 0x%x\n", "Illegal Instruction",
		address);
	INTCON1bits.BADOPERR = 0;
	PCTRAP = 0;
	k_fatal_halt(K_ERR_CPU_EXCEPTION);
}

/* Math error */
void EXCEPTION_HANDLER _MathErrorTrap(void)
{
	reason = INTCON4 & MATH_ERROR_MASK;
	address = PCTRAP;
	LOG_ERR("ERROR !!! Exception reason = %d, address = 0x%x\n", reason, address);
	INTCON4 &= ~(MATH_ERROR_MASK);
	PCTRAP = 0;
	k_fatal_halt(K_ERR_CPU_EXCEPTION);
}

/* Stack error */
void EXCEPTION_HANDLER _StackErrorTrap(void)
{
	const char *name = k_thread_name_get(_current);

	reason = INTCON1 & STACK_ERROR_MASK;
	address = PCTRAP;
	if (name == NULL) {
		name = "Unnamed";
	}
	LOG_ERR("ERROR !!! Exception reason = %d, address = 0x%x", reason, address);
	LOG_ERR("Thread : %p (%s)\n", _current, name);
	INTCON1bits.STKERR = 0;
	PCTRAP = 0;
	k_fatal_halt(K_ERR_STACK_CHK_FAIL);
}

/* Generic error */
void EXCEPTION_HANDLER _GeneralTrap(void)
{
	reason = INTCON5 & GENERAL_TRAP_MASK;
	address = PCTRAP;
	LOG_ERR("ERROR !!! Exception reason = %d, address = 0x%x\n", reason, address);
	INTCON5 &= ~(GENERAL_TRAP_MASK);
	PCTRAP = 0;
	k_fatal_halt(K_ERR_CPU_EXCEPTION);
}
