def convert_serial_to_parallel(filename):
    output_file = open(filename.split(".")[0]+"_parallel.c", "w+")
    input_file = open(filename, "r")
    braces_num = 0
    start = False
    for line in input_file:
        number_space = len(line) - len(line.lstrip())
        if(line.strip()[:3] == "for" and braces_num == 0):
            output_file.write(number_space * " " + "#pragma omp parallel for\n")
            start = True
        if(start):
            if(line.strip()[-1] == "{"):
                braces_num += 1
            if(line.strip()[-1] == "}"):
                braces_num -= 1
        output_file.write(line)
        if(start and braces_num == 0):
            output_file.write(number_space * " " + "#pragma omp barrier\n")
            start = False

if __name__ == "__main__":
    convert_serial_to_parallel("test_example/nested_for_loop_example.c")