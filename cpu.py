"""CPU functionality."""

import sys

HLT = 0O1
PRN = 71
LDI =130
MUL=162
POP=70
PUSH=69
CALL=80
RET=0b00010001
ADD=160
CMP=167
JMP=84
JEQ=0b01010101
JNE=0b01010110
AND=0b10101000
OR=0b10101010
XOR=0b10101011
NOT=0b01101001
MOD=0b10100100
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg=[0]* 8
        self.ram=[0]*256
        self.pc=0
        self.SP=7
        self.reg[self.SP]=0xf4
        self.FL=0b00000000
    


    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        
        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val=='':
                    continue
                v= int(string_val,2)
                self.ram[address]=v
                address +=1

    def ram_read(self,MAR):
        return self.ram[MAR]

        
    def ram_write(self,MDR,MAR):
        self.ram[MAR]=MDR
        
    
  
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op=="CMP":
           if self.reg[reg_a] < self.reg[reg_b]:
               self.FL = self.FL | 0b00000100
           if self.reg[reg_a] > self.reg[reg_b]:
               self.FL = self.FL | 0b00000010
           if self.reg[reg_a] == self.reg[reg_b]:
              self.FL = self.FL | 0b00000001
        elif op=="AND":
            self.reg[reg_a]&=reg_b
        elif op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b]==0:
                print(f'Operand b is 0')
                exit(1)
            else: 
                self.reg[reg_a] %= self.reg[reg_b]
        #elif op == "SUB": etc
        
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

    def run(self,):
        """Run the CPU."""
        """ It needs to read the memory address that's stored 
         in register PC, and store that result in IR, 
        the Instruction Register. 
        #This can just be a local variable in run()."""
        while True:
            IR = self.ram_read(self.pc)
            operand_a= self.ram_read(self.pc+1)
            operand_b= self.ram_read(self.pc+2)
            if IR==LDI:
                self.reg[operand_a]=operand_b
                self.pc+=3
            elif IR==PRN:
                value=self.reg[operand_a]
                print(value)
                self.pc+=2
            elif IR==MUL:
                op="MUL"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==AND:
                op="AND"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==OR:
                op="OR"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==XOR:
                op="XOR"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==MOD:
                op="MOD"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==NOT:
                op="NOT"
                b=0
                self.alu(op,operand_a,b)
                self.pc+=2
            elif IR==PUSH:
                self.reg[self.SP] -= 1
                reg_num = self.ram_read(self.pc+1)
                val = self.reg[reg_num]
                top_of_stack_addr = self.reg[self.SP]
                self.ram[top_of_stack_addr] = val
                self.pc += 2
            elif IR==POP:
            # Copy the value from the address pointed to by SP to the given register.
            # Increment SP.

                value=self.ram[self.reg[self.SP]]
                reg_num=operand_a
                self.reg[reg_num]=value
                self.reg[self.SP]+=1
                self.pc += 2
                
                
            elif IR==CALL:
                return_addr = self.pc + 2
        # Push it on the stack
                self.reg[self.SP] -= 1
                top_of_stack_addr = self.reg[self.SP]
                self.ram[top_of_stack_addr] = return_addr

        # Set the PC to the subroutine addr
                reg_num = self.ram[self.pc + 1]
                subroutine_addr = self.reg[reg_num]
                self.pc = subroutine_addr
            elif IR==RET:
                top_of_stack_addr = self.reg[self.SP]
                return_addr = self.ram[top_of_stack_addr]

        # Store it in the PC
                self.pc = return_addr
                self.reg[self.SP] += 1
            elif IR==ADD:
                op="ADD"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==CMP:
                op="CMP"
                self.alu(op,operand_a,operand_b)
                self.pc+=3
            elif IR==JMP:
                # Jump to the address stored in the given register.
                # Set the PC to the address stored in the given register.
                self.pc=self.reg[operand_a]
    
            elif IR==JEQ:
                if self.FL & 0b00000001==1:
                    self.pc=self.reg[operand_a]
                else:
                    self.pc+=2
            elif IR==JNE:
                if self.FL & 0b00000001 == 0:
                    self.pc=self.reg[operand_a]
                else:   
                    self.pc+=2
            elif IR==HLT:
                sys.exit(0)
            else:
                print(f'unknown instruction {IR} at address {self.pc}')
                exit(1)    



        
