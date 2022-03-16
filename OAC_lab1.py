import re
import re
from xml.dom.minidom import Element
import numpy as np

def get_data(data):  #revisar 
    data_output = {}

    for line in data:
        if line ==".data\n":
            continue
        aux = line.split()
        if not aux:
            continue
        elif line.split()[0]==".text":
            break

        teste = re.sub("[:., ]"," ",line)
        teste = re.sub(" "," ",teste)
        teste = teste.split()
        #[expr for item in lista]

        if(teste[0]!='data'):
            data_output[str(teste[0])]={'type':teste[1],'data':[int(value) for value in teste[2:]]}
    return (data_output)
def get_text(source):
    fix = ['lui','lw','sw','andi','ori','ori','xori','beq','bne','lb','slti','sb']
    instructions = []
    insctructions_text = source.split(".text\n")[1].replace("("," ").replace(")","").replace("Label: ","").splitlines()
    #print("here:",insctructions_text)

    for instruction in insctructions_text:
        instructions.append(instruction.replace(",","").split())
        
    return instructions

def get_code(data):
    data_output = {}

    for line in data:
        if line == ".reg\n":
            break
        aux = line.split()
        data_output[str(aux[0])]=[int(value,0) for value in aux[1:]]

    return(data_output)
def get_regRule(data):
    data_output = []
    flag = False
    
    for line in data:
        if line == ".reg\n":
            flag = True
            continue
        if not line:
            break
        if flag == True:
            aux = line.split()
            data_output.append(aux)
            
    return data_output
def get_reg(data):
    if (data[0] != "$"):
        return int(data)
    for element in regRule:
        if data == element[0]:
            return int(element[1],0)
    return 0
def get_equal(num,shift):
    return num * 2 ** shift
    
def get_hex(line,rule):
    tR =[26,21,16,11,6,0]          #deslocamento do tipo da instrução
    OpCode = rule[line[0]]

    if OpCode[0] == 0: # tipo R
        print("chegou")
        if OpCode[1]== 3: # sra
            return hex(get_equal(get_reg(line[2]),tR[2])+get_equal(get_reg(line[1]),tR[3])+get_equal(get_reg(line[3]),tR[4])+OpCode[1]) # Line: 2,1,3 // Op: 2,3,4
        if OpCode[1] == 7: # srav
            return hex(get_equal(get_reg(line[3]),tR[1])+get_equal(get_reg(line[2]),tR[2])+get_equal(get_reg(line[1]),tR[3])+OpCode[1]) # Line: 3,2,1 // Op: 1,2,3
        if OpCode[1] == 16 or OpCode[1] ==18:    # mtlo e mthi
            return hex(get_equal(get_reg(line[1]),tR[3])+OpCode[1]) # line: 1 // Op: 4(11)
        elif len(line) <= 3:  # instruções especiais / tamanho variado
            if OpCode[1] == 9:
                return  hex(get_equal(get_reg(line[1]),tR[1])+OpCode[1]+(get_equal(31,tR[3]) if len(line) == 2 else (get_equal(get_reg(line[2]),tR[1]))-get_equal(get_reg(line[1]),tR[1])+get_equal(get_reg(line[1]),tR[3]))) # JalR com apenas 1 registrador
            return hex(sum([get_equal(get_reg(line[i+1]),tR[i+1]) for i in range(len(line)-1)])+OpCode[1]) # Line: 1,2,3 // Op: 1,2,3
        elif OpCode[1] == 0 or OpCode[1] == 2: # Sll e srl
            return hex(get_equal(get_reg(line[2]),tR[2])+get_equal(get_reg(line[1]),tR[3])+get_equal(get_reg(line[3]),tR[4])+OpCode[1]) # Line: 2,1,3 // Op: 2,3,4
        return hex(get_equal(get_reg(line[2]),tR[1])+get_equal(get_reg(line[3]),tR[2])+get_equal(get_reg(line[1]),tR[3])+OpCode[1])  # Line: 2,3,1  // Op: 1,2,3
    elif OpCode[0] == 2 or OpCode[0] == 3: # Tipo J
        return hex(get_equal(int(OpCode[0]),26)+np.right_shift(int(line[1],0),2))
    elif OpCode[0] == 0: # Instrução Li 
        
        return None
    elif OpCode[0] == 17: # Instruções .fmt
        return hex(sum([get_equal(get_reg(line[j+1]),tR[i+2]) for i,j in zip(range(len(line)),range(len(line)-2,-1,-1))])+get_equal(int(OpCode[0]),tR[0])+int(OpCode[1])+(get_equal(17,tR[1]) if line[0][-1] == "d" else get_equal(16,tR[1]))) # Line: 3,2,1 // Op: 1,2,3
    else: # Instruções tipo I
        if OpCode[0] == 43 or OpCode[0] == 35 or OpCode[0] == 32 or OpCode[0] == 40: # Lw,Sw,Lb e Sb
            return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[3]),tR[1])+get_equal(get_reg(line[1]),tR[2])+ int(line[2]))  # Line: 3,1,2 // OP: 0,1,2
        elif OpCode[0] == 4 or OpCode[0] == 5:  # beq e bne
            return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[1]),tR[1])+get_equal(get_reg(line[2]),tR[2])+65536-int(line[3],0)*-1)  # Line: 0,1,2,3 // OP: 0,1,2,3
        elif OpCode[0] == 15: # lui
            return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[1]),tR[2])+int(line[2],tR[5])) # Line: 1,2 // OP: 2,5
        elif OpCode[0] == 28 and (OpCode[1] == 0 or OpCode[1] == 5): # Madd e Msubu
            print("here")
            return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[1]),tR[1])+get_equal(get_reg(line[2]),tR[2])+OpCode[1]) #Line: 2,3
        elif OpCode[0] == 28 and OpCode[1] == 2: # mul
            return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[2]),tR[1])+get_equal(get_reg(line[3]),tR[2])+get_equal(get_reg(line[1]),tR[3])+OpCode[1]) # Line: 2,3,1 
        elif OpCode[0] == 28: # clo
            return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[1]),tR[3])+get_equal(get_reg(line[2]),tR[1])+OpCode[1]) # Line: 1,2 // OP: 3,2
        elif OpCode[0] == 1: # bgez e bgezal
            return hex(get_equal(OpCode[0],tR[0])+ get_equal(get_reg(line[1]),tR[1])+ get_equal(OpCode[1],tR[2])+((65536-(get_equal(get_reg(line[2]),tR[5])*-1)) if get_reg(line[2])<0 else int((line[2]),0))) # Line: op,1,op,2 // OP: 0,1,2,5
        return hex(get_equal(OpCode[0],tR[0])+get_equal(get_reg(line[2]),tR[1])+get_equal(get_reg(line[1]),tR[2])+((65536-(get_equal(get_reg(line[3]),tR[5])*-1)) if get_reg(line[3])<0 else int((line[3]),0))) # Addiu e Slti OP: 2,1,IMM



path = "arquivos-exemplos/"
data_input = open(path+"example_saida.asm",'r').readlines()
data_input2 = open(path+"dados2.txt",'r').readlines()

instructions = get_text(''.join(data_input))
rule = get_code(data_input2)
regRule = get_regRule(data_input2)
teste = ['sub.s', '$f1','$f2','$f3']
teste2 = ['sb', '$t1','100', '$t2']
teste3 = ['msubu', '$t1','$t2']


#print(rule,regRule)
#print("len:",len(teste))

#print(instructions[1])
print(get_hex(teste,rule))
#print(get_hex(teste2,rule))
#print(get_reg(instructions[5][3]))



#for n in range(len(instructions)):
#   print(instructions[n])
#    print(get_hex(instructions[n],rule))