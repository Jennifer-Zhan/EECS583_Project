import clang.cindex
import sys
clang.cindex.Config.set_library_path("/Library/Developer/CommandLineTools/usr/lib")

def get_print_lines(filename):
    print_line = []
    idx = clang.cindex.Index.create()
    tu = idx.parse(filename)
    for token in tu.cursor.get_tokens():
        #print(token.spelling)
        if(token.spelling == "print" or token.spelling == "printf"):
            #print(token.location.line)
            print_line.append(int(token.location.line) - 1)
    return print_line


def convert_serial_to_parallel(filename, print_line):
    output_file = open(filename.split(".")[0]+"_parallel.c", "w+")
    input_file = open(filename, "r")
    current_line_num = 0
    braces_num = 0
    start = False
    print_num = 0
    output_file.write("#include <omp.h>\n")
    for line in input_file:
        current_line_num += 1
        number_space = len(line) - len(line.lstrip())
        add_critical = False
        if(line.strip()[:3] == "for" and braces_num == 0):
            #print(str(current_line_num)+" "+str(print_line[print_num]))
            if(len(print_line) == 0 or current_line_num != print_line[print_num]):
                output_file.write(number_space * " " + "#pragma omp parallel for\n")
                start = True
            #else:
                #print_num += 1
                #print(str(print_num)+" "+str(current_line_num))
        elif(line.strip()[:5] == "print"):
            print_num += 1
            # print(str(print_num)+" "+str(current_line_num))
        if(start):
            # add lock when there is +=
            # print(line.strip().split())
            if "+=" in line.strip().split():
                output_file.write(number_space * " " + "#pragma omp critical\n" + number_space * " " + "{\n")
                add_critical = True
            if(line.strip()[-1] == "{"):
                braces_num += 1
            if(line.strip()[-1] == "}"):
                braces_num -= 1
        output_file.write(line)
        if(add_critical):
            output_file.write(number_space * " " + "}\n")
        if(start and braces_num == 0):
            output_file.write(number_space * " " + "#pragma omp barrier\n")
            start = False

if __name__ == "__main__":
    filename = sys.argv[1]
    print_line = get_print_lines(filename)
    # print(print_line)
    convert_serial_to_parallel(filename, print_line)