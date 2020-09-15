"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.flags = [0] * 8
        self.looping = False
        self.file = sys.argv
        self.sp = 6
        self.instruction_set = {
            'HLT': 0b00000001,
            'LDI': 0b10000010,
            'PRN': 0b01000111,
            'ADD': 0b10100000,
            'MUL': 0b10100010,
            'PUSH': 0b01000101,
            'POP': 0b01000110,
            'CMP': 0b10100111,
            'JMP': 0b01010100,
            'JEQ': 0b01010101,
            'JNE': 0b01010110,
            'CALL': 0b01010000,
            'RET': 0b00010001,
        }

    def load(self, program=[]):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            print("Usage example_cpu.py filename")

        program = []

        with open(sys.argv[1]) as file:
            for line in file:
                split_line = line.split('#')[0].strip()
                if split_line == "":
                    continue
                else:
                    program.append(int(split_line, 2))

        address = 0

        # split program
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr): # memory address register, memory data register
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == self.instruction_set['ADD']:
            new_val = self.reg[reg_a] + self.reg[reg_b]
            self.reg[reg_a] = new_val
            self.pc += 3
        elif op == self.instruction_set['MUL']:
            new_val = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] = new_val
            self.pc += 3
        elif op == self.instruction_set['CMP']:
            if reg_a == reg_b:
                self.flags = 0b00000001 # set e flag
            elif reg_a > reg_b:
                self.flags = 0b00000010 # set g flag
            elif reg_a < reg_b:
                self.flags = 0b00000100 # set l flag

            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # reset registers
        self.looping = True

        while self.looping:
            instruction_register = self.ram_read(self.pc)
            is_alu = instruction_register >> 5 & 0b1
            num_operands = instruction_register >> 6
            operand_a = self.ram_read(self.pc + 1)

            if num_operands == 2:
                operand_b = self.ram_read(self.pc + 2)
            # self.trace()

            if is_alu == 1: # if 1, needs to pass through the alu
                self.alu(instruction_register, self.reg[operand_a], self.reg[operand_b])

            elif instruction_register == self.instruction_set['HLT']:
                self.looping = False

            elif instruction_register == self.instruction_set['LDI']:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif instruction_register == self.instruction_set['PRN']:
                print(self.reg[operand_a])
                self.pc += 2

            elif instruction_register == self.instruction_set['PUSH']:
                val_in_reg = self.reg[operand_a]
                self.reg[self.sp] -= 1
                self.ram_write(self.reg[self.sp], val_in_reg)
                self.pc += 2

            elif instruction_register == self.instruction_set['POP']:
                val_from_ram = self.ram_read(self.reg[self.sp])
                self.reg[operand_a] = val_from_ram
                self.reg[self.sp] += 1
                self.pc += 2

            elif instruction_register == self.instruction_set['CALL']:
                given_register = self.reg[operand_a]
                self.sp -= 1
                return_address = self.pc + 2
                new_address = self.reg[self.sp]
                self.ram[new_address] = return_address
                self.pc = given_register

            elif instruction_register == self.instruction_set['RET']:
                new_address = self.reg[self.sp]
                return_address = self.ram[new_address]
                self.reg[self.sp] += 1
                self.pc = return_address

            elif instruction_register == self.instruction_set['JMP']:
                self.pc = self.reg[operand_a]

            elif instruction_register == self.instruction_set['JEQ']:
                flg = self.flags & 0b00000001 # 1
                if flg == 1: # are equal
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            elif instruction_register == self.instruction_set['JNE']:
                flg = self.flags & 0b00000001 # 0
                if flg == 0: # not equal
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2

            else:
                print(f"Unknown instuction {instruction_register} at {self.pc}")
