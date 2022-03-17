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
def get_reg(data):   # retorna o número do registrador ex: $zero = 0
    if (data[0] != "$"):
        return int(data)
    for element in regRule:
        if data == element[0]:
            return int(element[1],0)
    print("An exception occurred in Register:",data)
    return None
def get_equal(num,shift):
    return num * 2 ** shift
def get_hex(line,rule):
    tR =[26,21,16,11,6,0]          #deslocamento do tipo da instrução
    constLi = [1006698497,875036672]  # constante usadas para fazer a instrução Li
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
                return hex(constLi[0]),hex(constLi[1]+int(line[2]))

        Op = rule[line[0]]
        if Op[0] == 0: # tipo R
            if Op[1]== 3: # sra
                return hex(get_equal(get_reg(line[2]),tR[2])+get_equal(get_reg(line[1]),tR[3])+get_equal(get_reg(line[3]),tR[4])+Op[1]) # Line: 2,1,3 // Op: 2,3,4
            if Op[1] == 7: # srav
                return hex(get_equal(get_reg(line[3]),tR[1])+get_equal(get_reg(line[2]),tR[2])+get_equal(get_reg(line[1]),tR[3])+Op[1]) # Line: 3,2,1 // Op: 1,2,3
            if Op[1] == 16 or Op[1] ==18:    # mtlo e mthi
                return hex(get_equal(get_reg(line[1]),tR[3])+Op[1]) # line: 1 // Op: 4(11)
            elif len(line) <= 3:  # instruções especiais / tamanho variado
                if Op[1] == 9:
                    return  hex(get_equal(get_reg(line[1]),tR[1])+Op[1]+(get_equal(31,tR[3]) if len(line) == 2 else (get_equal(get_reg(line[2]),tR[1]))-get_equal(get_reg(line[1]),tR[1])+get_equal(get_reg(line[1]),tR[3]))) # JalR com apenas 1 registrador
                return hex(sum([get_equal(get_reg(line[i+1]),tR[i+1]) for i in range(len(line)-1)])+Op[1]) # Line: 1,2,3 // Op: 1,2,3
            elif Op[1] == 0 or Op[1] == 2: # Sll e srl
                return hex(get_equal(get_reg(line[2]),tR[2])+get_equal(get_reg(line[1]),tR[3])+get_equal(get_reg(line[3]),tR[4])+Op[1]) # Line: 2,1,3 // Op: 2,3,4
            return hex(get_equal(get_reg(line[2]),tR[1])+get_equal(get_reg(line[3]),tR[2])+get_equal(get_reg(line[1]),tR[3])+Op[1])  # Line: 2,3,1  // Op: 1,2,3
        elif Op[0] == 2 or Op[0] == 3: # Tipo J
            return hex(get_equal(int(Op[0]),26)+np.right_shift(int(line[1],0),2))
        elif Op[0] == 17: # Instruções .fmt
            return hex(sum([get_equal(get_reg(line[j+1]),tR[i+2]) for i,j in zip(range(len(line)),range(len(line)-2,-1,-1))])+get_equal(int(Op[0]),tR[0])+int(Op[1])+(get_equal(17,tR[1]) if line[0][-1] == "d" else get_equal(16,tR[1]))) # Line: 3,2,1 // Op: 1,2,3
        else: # Instruções tipo I
            if Op[0] == 43 or Op[0] == 35 or Op[0] == 32 or Op[0] == 40: # Lw,Sw,Lb e Sb
                return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[3]),tR[1])+get_equal(get_reg(line[1]),tR[2])+ int(line[2]))  # Line: 3,1,2 // OP: 0,1,2
            elif Op[0] == 4 or Op[0] == 5:  # beq e bne
                return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[1]),tR[1])+get_equal(get_reg(line[2]),tR[2])+65536-int(line[3],0)*-1)  # Line: 0,1,2,3 // OP: 0,1,2,3
            elif Op[0] == 15: # lui
                return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[1]),tR[2])+int(line[2],tR[5])) # Line: 1,2 // OP: 2,5
            elif Op[0] == 28 and (Op[1] == 0 or Op[1] == 5): # Madd e Msubu
                print("here")
                return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[1]),tR[1])+get_equal(get_reg(line[2]),tR[2])+Op[1]) #Line: 2,3
            elif Op[0] == 28 and Op[1] == 2: # mul
                return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[2]),tR[1])+get_equal(get_reg(line[3]),tR[2])+get_equal(get_reg(line[1]),tR[3])+Op[1]) # Line: 2,3,1 
            elif Op[0] == 28: # clo
                return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[1]),tR[3])+get_equal(get_reg(line[2]),tR[1])+Op[1]) # Line: 1,2 // OP: 3,2
            elif Op[0] == 1: # bgez e bgezal
                return hex(get_equal(Op[0],tR[0])+ get_equal(get_reg(line[1]),tR[1])+ get_equal(Op[1],tR[2])+((65536-(get_equal(get_reg(line[2]),tR[5])*-1)) if get_reg(line[2])<0 else int((line[2]),0))) # Line: op,1,op,2 // OP: 0,1,2,5
            return hex(get_equal(Op[0],tR[0])+get_equal(get_reg(line[2]),tR[1])+get_equal(get_reg(line[1]),tR[2])+((65536-(get_equal(get_reg(line[3]),tR[5])*-1)) if get_reg(line[3])<0 else int((line[3]),0))) # Addiu e Slti OP: 2,1,IMM
    except:
        print("An exception occurred in instruction:",line)
        return None


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
def get_A(instructions, rule):
    const_tamI = 4294967295
    text = []
    for idx in range(len(instructions)):
        codeM = get_hex(instructions[idx],rule)
        if  codeM == None:  # caso ocorra um erro na instrução
            text.append((hex(const_tamI),"Instruction error"))
        elif type(codeM) == str and int(codeM,0) >= const_tamI: # caso ocorra um overflow na instrução
            print("Instruction overflow")
            text.append((hex(const_tamI),"Instruction error"))
        else:
            text.append((codeM,instructions[idx]))
    return text
    
def save_text_saida(data):
    print("oi mundo")
    return 0


#------------------------ Main ---------------------------
path = ["input/","arquivos/"]
data_input = open(path[0]+"example_saida.asm",'r').readlines()
data_input2 = open(path[1]+"dados.txt",'r').readlines()

instructions = get_text(''.join(data_input)) # gera as instruções
data = get_data(data_input)         # gera um dicionario para o .data
rule = get_code(data_input2)        # dicionario de funções
regRule = get_regRule(data_input2)  # dicionario de registradores 

save_data_saida(data)
instructions2 = [['add', '$zero', '$zero', '$zero']]
text = get_A(instructions,rule)
for itens in range(len(text)):
    if type(text[itens]) != tuple:
        print(text[itens][0].rjust(8, '0'),text[itens][1])
    else:
        print(text[itens][0],text[itens][1])
    


#data_values.append(np.base_repr(int(element), base = 16).rjust(8,'0'))

#text_out = []
#for n in range(len(instructions)):
    #text_out.append( (instructions[n],get_hex(instructions[n],rule)) )
#    text_out.append( np.base_repr(int(n), base = 16).rjust(8,'0'))

#for itens in range(len(text_out)):#
#    print(text_out[itens])

