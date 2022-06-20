#UnB - Universidade de Brasília
#Aluno:     Alexander Matheus de Melo Lima - 120108534
#Aluno:     Gabriel Martins de Almeida - 190013371
#Aluno:     Pedro Chaves - 170153835
import re
import re
from xml.dom.minidom import Element
import numpy as np

def get_data(data): 
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

        if(teste[0]!='data'):
            data_output[str(teste[0])]={'type':teste[1],'data':[int(value) for value in teste[2:]]}
    return (data_output)
def get_text(source):
    instructions = []
    insctructions_text = source.split(".text\n")[1].replace("("," ").replace(")","").replace("Label: ","").splitlines()

    for instruction in insctructions_text:
        instructions.append(instruction.replace(",","").split())
        
    return instructions

def get_op(data):
    data_output = {}

    for line in data:
        if line == ".reg\n":
            break
        aux = line.split()
        data_output[str(aux[0])]=[int(value,0) for value in aux[1:]]

    return(data_output)
def get_reg_rule(data):
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
def get_reg(data):   # retorna o número do registrador ex: $zero = 0
    if (data[0] != "$"):
        return int(data)
    for element in reg_rule:
        if data == element[0]:
            return int(element[1],0)
    print("An exception occurred in Register:",data)
    return None
def sll(num,shift):
    return num * 2 ** shift
def get_hex(line,rule):
    tR =[26,21,16,11,6,0]          #deslocamento do tipo da instrução
    const_li = [1006698497,875036672]  # constante usadas para fazer a instrução Li
    try:
        for i in range(len(line)): # Transforma hexadecimal em decimal
            if line[i].find("0x") != -1 and i!=0:
                line[i] = str(int(line[i],0))
        if line[0]=='li': # Pseudo instrução Li.
            if int(line[2])<=32767:   # valor aceito na faixa da instrução addiu
                return get_hex(['addiu', line[1], '$zero', line[2]],rule)
            if int(line[2])<=65535:  # valor que precisa de apenas o Ori
                return hex(872939520+int(line[2]))
            else:  # valor que precisa de duas instruções.
                return hex(const_li[0]),hex(const_li[1]+int(line[2]))

        op = rule[line[0]]
        if op[0] == 0: # tipo R
            if op[1]== 3: # sra
                return hex(sll(get_reg(line[2]),tR[2])+sll(get_reg(line[1]),tR[3])+sll(get_reg(line[3]),tR[4])+op[1]) # Line: 2,1,3 // Op: 2,3,4
            if op[1] == 7: # srav
                return hex(sll(get_reg(line[3]),tR[1])+sll(get_reg(line[2]),tR[2])+sll(get_reg(line[1]),tR[3])+op[1]) # Line: 3,2,1 // Op: 1,2,3
            if op[1] == 16 or op[1] ==18:    # mtlo e mthi
                return hex(sll(get_reg(line[1]),tR[3])+op[1]) # line: 1 // Op: 4(11)
            elif len(line) <= 3:  # instruções especiais / tamanho variado
                if op[1] == 9:
                    return  hex(sll(get_reg(line[1]),tR[1])+op[1]+(sll(31,tR[3]) if len(line) == 2 else (sll(get_reg(line[2]),tR[1]))-sll(get_reg(line[1]),tR[1])+sll(get_reg(line[1]),tR[3]))) # JalR com apenas 1 registrador
                return hex(sum([sll(get_reg(line[i+1]),tR[i+1]) for i in range(len(line)-1)])+op[1]) # Line: 1,2,3 // Op: 1,2,3
            elif op[1] == 0 or op[1] == 2: # Sll e srl
                return hex(sll(get_reg(line[2]),tR[2])+sll(get_reg(line[1]),tR[3])+sll(get_reg(line[3]),tR[4])+op[1]) # Line: 2,1,3 // Op: 2,3,4
            return hex(sll(get_reg(line[2]),tR[1])+sll(get_reg(line[3]),tR[2])+sll(get_reg(line[1]),tR[3])+op[1])  # Line: 2,3,1  // Op: 1,2,3
        elif op[0] == 2 or op[0] == 3: # Tipo J
            return hex(sll(int(op[0]),26)+np.right_shift(int(line[1],0),2))
        elif op[0] == 17: # Instruções .fmt
            return hex(sum([sll(get_reg(line[j+1]),tR[i+2]) for i,j in zip(range(len(line)),range(len(line)-2,-1,-1))])+sll(int(op[0]),tR[0])+int(op[1])+(sll(17,tR[1]) if line[0][-1] == "d" else sll(16,tR[1]))) # Line: 3,2,1 // Op: 1,2,3
        else: # Instruções tipo I
            if op[0] == 43 or op[0] == 35 or op[0] == 32 or op[0] == 40: # Lw,Sw,Lb e Sb
                return hex(sll(op[0],tR[0])+sll(get_reg(line[3]),tR[1])+sll(get_reg(line[1]),tR[2])+ int(line[2]))  # Line: 3,1,2 // OP: 0,1,2
            elif op[0] == 4 or op[0] == 5:  # beq e bne
                return hex(sll(op[0],tR[0])+sll(get_reg(line[1]),tR[1])+sll(get_reg(line[2]),tR[2])+65536-int(line[3],0)*-1)  # Line: 0,1,2,3 // OP: 0,1,2,3
            elif op[0] == 15: # lui
                return hex(sll(op[0],tR[0])+sll(get_reg(line[1]),tR[2])+int(line[2],tR[5])) # Line: 1,2 // OP: 2,5
            elif op[0] == 28 and (op[1] == 0 or op[1] == 5): # Madd e Msubu
                return hex(sll(op[0],tR[0])+sll(get_reg(line[1]),tR[1])+sll(get_reg(line[2]),tR[2])+op[1]) #Line: 2,3
            elif op[0] == 28 and op[1] == 2: # mul
                return hex(sll(op[0],tR[0])+sll(get_reg(line[2]),tR[1])+sll(get_reg(line[3]),tR[2])+sll(get_reg(line[1]),tR[3])+op[1]) # Line: 2,3,1 
            elif op[0] == 28: # clo
                return hex(sll(op[0],tR[0])+sll(get_reg(line[1]),tR[3])+sll(get_reg(line[2]),tR[1])+op[1]) # Line: 1,2 // OP: 3,2
            elif op[0] == 1: # bgez e bgezal
                return hex(sll(op[0],tR[0])+ sll(get_reg(line[1]),tR[1])+ sll(op[1],tR[2])+((65536-(sll(get_reg(line[2]),tR[5])*-1)) if get_reg(line[2])<0 else int((line[2]),0))) # Line: op,1,op,2 // OP: 0,1,2,5
            return hex(sll(op[0],tR[0])+sll(get_reg(line[2]),tR[1])+sll(get_reg(line[1]),tR[2])+((65536-(sll(get_reg(line[3]),tR[5])*-1)) if get_reg(line[3])<0 else int((line[3]),0))) # Addiu e Slti OP: 2,1,IMM
    except:
        print("An exception occurred in instruction:",line)
        return None

def get_assemble(instructions, rule):
    const_tam = 4294967295
    text = []
    for idx in range(len(instructions)):
        machine_code = get_hex(instructions[idx],rule)
        if  machine_code == None:  # caso ocorra um erro na instrução
            text.append((hex(const_tam),"Instruction error"))
        elif type(machine_code) == str and int(machine_code,0) >= const_tam: # caso ocorra um overflow na instrução
            print("Instruction overflow")
            text.append((hex(const_tam),"Instruction error"))
        else:
            if type(machine_code) != str:
                text.append((machine_code[0],instructions[idx]))
                text.append((machine_code[1],[]))
            else:    
                text.append((machine_code,instructions[idx]))
    return text
def save_data_saida(data):

    output_data = open("output/saida_data.mif",'w')
    address_data = []
    data_values=[]
    index = 0
    DEFAULT_HEADER = """DEPTH = 16384;
WIDTH = 32;
ADDRESS_RADIX = HEX;
DATA_RADIX = HEX;
CONTENT
BEGIN\n\n""" 
    output_data.writelines(DEFAULT_HEADER)

    for key in data:
        for element in data[key]['data']:
            data_values.append(np.base_repr(int(element), base = 16).rjust(8,'0'))

    for index in range(0,len(data_values)):
        address_data.append(np.base_repr(index,base=16).rjust(8,'0'))

    for i,j in zip(address_data,data_values):
        output_data.writelines(i + ' : ' + j + '\n')

    output_data.writelines('\nEND;')
    print('Arquivo saida_data.mif salvo com sucesso na pasta output!')    
def save_text_saida(data,data2):
    DEFAULT_HEADER ="""DEPTH = 4096;
WIDTH = 32;
ADDRESS_RADIX = HEX;
DATA_RADIX = HEX;
CONTENT
BEGIN\n
"""
    output_text = open("output/saida_text.mif",'w')
    instructions_line = ""
    instructions = []

    for idx in range(len(data)):
        instructions_line = str((np.base_repr(idx,base=16).rjust(8,'0'))+" : ")
        instructions_line = instructions_line + str((np.base_repr(int(data[idx][0],0),base=16).rjust(8, '0')))
        instructions.append(instructions_line)

    flag = False
    idx=0    
    for i in range(len(data2)):
        if flag == True:
            if data2[i].find("li") != -1:
                instructions[idx]= instructions[idx]+";  % "+ str(i+1)+": "+data2[i][:-1]+" %"
                instructions[idx+1]= instructions[idx+1]+";"
                idx+=2
            elif len(data2[i])>0:
                instructions[idx]= instructions[idx]+";  % "+ str(i+1)+": "+data2[i][:-1]+" %"
                idx+=1
        elif data2[i].find(".text") != -1:
            flag = True

    output_text.write(DEFAULT_HEADER)
    for idx in range(len(instructions)):
        output_text.writelines(instructions[idx]+"\n")
    output_text.writelines("\nEND;")

    for itens in range(len(instructions)):
        print(instructions[itens])

    print("Arquivo saida_text.mif salvo com sucesso na pasta output!")

path = ["input/","arquivos/"]
data_input = ((open(path[0]+"example_saida.asm",'r').readlines(),open(path[1]+"dados.txt",'r').readlines()))

instructions = get_text(''.join(data_input[0])) # gera as instruções
data = get_data(data_input[0])                  # gera um dicionario para o .data no formato: {'name': {'type': 'word', 'data': [1, 2, 3]}}
op_rule = get_op(data_input[1])                 # dicionario de instruções para o OPcode e Funct
reg_rule = get_reg_rule(data_input[1])          # dicionario de registradores 

save_data_saida(data)
text = get_assemble(instructions,op_rule)
save_text_saida(text,data_input[0])