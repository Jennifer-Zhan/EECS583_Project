import sys
import re
import os

def convert_serial_to_pthreads(file_path, num_threads):
  lines = []

  with open(file_path, "r") as file:
    for line in file:
      lines.append(line.strip())
  
  new_lines = []
  new_lines.append("#define _POSIX_C_SOURCE 200112L")
  new_lines.append("#include <pthread.h>")
  new_lines.append("#include <stdio.h>")
  new_lines.append("#include <stdlib.h>")
  new_lines.append('#include "pthreads_barrier.h"')
  
  new_lines.append("#define ADD_LOCK_A(idx, code) pthread_mutex_lock(locks_A + (idx)); code pthread_mutex_unlock(locks_A + (idx));")
  new_lines.append("#define ADD_LOCK_Ar(idx, code) pthread_mutex_lock(locks_Ar + (idx)); code pthread_mutex_unlock(locks_Ar + (idx));")
  new_lines.append("#define ADD_LOCK_Aw(idx, code)  pthread_mutex_lock(locks_Aw + (idx)); code  pthread_mutex_unlock(locks_Aw + (idx));")
  new_lines.append("#define ADD_LOCK_Anp(idx, code) pthread_mutex_lock(locks_Anp + (idx)); code  pthread_mutex_unlock(locks_Anp + (idx));")
  new_lines.append("#define ADD_LOCK_Anx(idx, code) pthread_mutex_lock(locks_Anx + (idx)); code   pthread_mutex_unlock(locks_Anx + (idx));")
  new_lines.append("#define ADD_LOCK_dist_w(code) pthread_mutex_lock(&lock_dist_w); code   pthread_mutex_unlock(&lock_dist_w);" )
  new_lines.append("#define ADD_LOCK_w(code) pthread_mutex_lock(&lock_w); code   pthread_mutex_unlock(&lock_w);" )
  
  pattern_A = r'int\s+A\[\d+\]\s+=\s+\{[^\}]+\}'
  pattern_A_num =  r'int\s+A\[(\d+)\]\s*=\s*\{[^\}]*\}'
  pattern_Aw = r'int\s+Aw\[\d+\]\s+=\s+\{[^\}]+\}'
  pattern_Ar = r'int\s+Ar\[\d+\]\s+=\s+\{[^\}]+\}'
  pattern_Anp = r'int\s+Anp\[\d+\]\s+=\s+\{[^\}]+\}'
  pattern_Anx = r'int\s+Anx\[\d+\]\s+=\s+\{[^\}]+\}'
  pattern_for = r'for\s*\(\s*[a-zA-Z_]\w*\s*=\s*(\d+)\s*;\s*[a-zA-Z_]\w*\s*<\s*(\d+)\s*;\s*[a-zA-Z_]\w*\s*\+\+\s*\)'
  pattern_global_idx_A = r'A\[(([A-Za-z])\[(i)\]|\b(i\s*[\+\-\*]\s*\d+)\b)\]'
  pattern_global_idx_Ar = r'Ar\[(([A-Za-z])\[(i)\]|\b(i\s*[\+\-\*]\s*\d+)\b)\]'
  pattern_global_idx_Aw = r'Aw\[(([A-Za-z])\[(i)\]|\b(i\s*[\+\-\*]\s*\d+)\b)\]'
  pattern_global_idx_Anp = r'Anp\[(([A-Za-z])\[(i)\]|\b(i\s*[\+\-\*]\s*\d+)\b)\]'
  pattern_global_idx_Anx = r'Anx\[(([A-Za-z])\[(i)\]|\b(i\s*[\+\-\*]\s*\d+)\b)\]'
  
  
  num_for = 0
  iter_var = 0
  iter_val = 0
  
  global_idx_var = []
  major_for_lineNum = 0
  cur_lineNum = 0;
  
  global_line = []
  major_for_line =[]
  locked_for_lines = []
  major_for_line_locked = []
  analysis_line =[]
  bracket_depth = 0
  start = False
  stop = False
  for_start = False
  for_stop = False
  ana_start = False
  ana_stop = False
  for line in lines:
    if ("int i" in line):
      stop = True
    if start and not stop:
      global_line.append(line)
    if "{" in line and not start:
      start = True
    if re.match(pattern_A_num, line):
      match = re.search(pattern_A_num, line)
      num_elements = int(match.group(1))
      new_lines.append("#define NUM_ELEMS "+ str(int(num_elements)))
    if for_start and not for_stop:
      if "{" in line:
        bracket_depth += 1
      if "}" in line:
        bracket_depth -= 1
      major_for_line.append(line)
      if bracket_depth == 0:
        for_stop = True
    if ("for" in line and num_for == 0):
      major_for_lineNum = cur_lineNum
      match = re.search(pattern_for, line)
      if match:
        iter_var = match.group(1)
        iter_val = int(match.group(2))
        num_for += 1
        num_iter = int(match.group(2))
        new_lines.append("#define NUM_ITER " + str(int(iter_val)))
        new_lines.append("#define NUM_THREADS "+ str(int(num_threads)))
        for_start = True
        if "{" in line:
          bracket_depth += 1
          locked_for_lines.append("{")
    
  new_lines.extend(global_line)
  new_lines.append("pthread_barrier_t barrier;")
  new_lines.append("pthread_mutex_t locks_A[NUM_ELEMS];")
  new_lines.append("pthread_mutex_t locks_Ar[NUM_ELEMS];")
  new_lines.append("pthread_mutex_t locks_Aw[NUM_ELEMS];")
  new_lines.append("pthread_mutex_t locks_Anp[NUM_ELEMS];")
  new_lines.append("pthread_mutex_t locks_Anx[NUM_ELEMS];")
  new_lines.append("pthread_mutex_t lock_dist_w;")
  new_lines.append("pthread_mutex_t lock_w;")
  
  new_lines.append("struct ThreadArgs {int arg1;int arg2;};")
  
  pattern_A =  r'A\w*\[([^][]*(?:\[[^][]*\])?[^][]*)\]'
  pattern_shadow_r =  r'Ar\w*\[([^][]*(?:\[[^][]*\])?[^][]*)\]'
  pattern_shadow_w =  r'Aw\w*\[([^][]*(?:\[[^][]*\])?[^][]*)\]'
  pattern_shadow_np =  r'Anp\w*\[([^][]*(?:\[[^][]*\])?[^][]*)\]'
  pattern_shadow_nx =  r'Anx\w*\[([^][]*(?:\[[^][]*\])?[^][]*)\]'
  
 
  # new_lines
  for idx, line in enumerate( major_for_line):
    replaced = False;
    matches = re.findall(pattern_A, line)
    if matches:
      variable_names = matches
      existing_var_list = []
      for match_case in matches:
        variable_names = match_case
        if (variable_names not in existing_var_list and "Awi" not in line):
          # print(variable_names)
          newline = "ADD_LOCK_A(" + variable_names + ","+ line + ")"
          existing_var_list.append(variable_names)
          locked_for_lines.append(newline)
          replaced = True
          # print(line)
  
    matches = re.findall(pattern_shadow_r, line)
    if matches:
      variable_names = matches
      existing_var_list = []
      for match_case in matches:
        variable_names = match_case
        if (variable_names not in existing_var_list and "Awi" not in line):
          # print(variable_names)
          newline = "ADD_LOCK_Ar(" + variable_names + ","+ line + ")"
          existing_var_list.append(variable_names)
          locked_for_lines.append(newline)
          replaced = True
          # print(line)
          
    matches = re.findall(pattern_shadow_w, line)
    if matches:
      variable_names = matches
      existing_var_list = []
      for match_case in matches:
        variable_names = match_case
        if (variable_names not in existing_var_list and "Awi" not in line):
          # print(variable_names)
          newline = "ADD_LOCK_Aw(" + variable_names + ","+ line + ")"
          existing_var_list.append(variable_names)
          locked_for_lines.append(newline)
          replaced = True
          # print(line)  
    
    matches = re.findall(pattern_shadow_np, line)
    if matches:
      variable_names = matches
      existing_var_list = []
      for match_case in matches:
        variable_names = match_case
        if (variable_names not in existing_var_list and "Awi" not in line):
          # print(variable_names)
          newline = "ADD_LOCK_Anp(" + variable_names + ","+ line + ")"
          existing_var_list.append(variable_names)
          locked_for_lines.append(newline)
          replaced = True
          # print(line)
  
    matches = re.findall(pattern_shadow_nx, line)
    if matches:
      variable_names = matches
      existing_var_list = []
      for match_case in matches:
        variable_names = match_case
        if (variable_names not in existing_var_list and "Awi" not in line):
          # print(variable_names)
          newline = "ADD_LOCK_Anx(" + variable_names + ","+ line + ")"
          existing_var_list.append(variable_names)
          locked_for_lines.append(newline)
          replaced = True
          # print(line)
  
    if "write_counter += 1;" in line:
      replaced=True
      newline = "ADD_LOCK_w(write_counter += 1;)"
      locked_for_lines.append(newline)
      
    if not replaced:
      locked_for_lines.append(line)
  # locked_for_lines
  
  thread_func_lines = ["void *thread_func(void *arg) {", "struct ThreadArgs *threadArgs = (struct ThreadArgs *)arg;", "int i_start = threadArgs->arg1; int i_end = threadArgs->arg2;"]
  thread_func_lines.append("for (int i = i_start; i < i_end; i++)")
  if ("{" not in locked_for_lines[0]):
    thread_func_lines.append("{")
  thread_func_lines.extend(locked_for_lines)
  thread_func_lines.append("pthread_barrier_wait(&barrier);pthread_exit(NULL);")
  thread_func_lines.append("}")
  
  new_lines.extend(thread_func_lines);
  
  main_lines = ["int main(int argc, char **argv) {"]
  main_lines.append("pthread_t thread[NUM_THREADS];")
  main_lines.append("for (int i = 0; i < NUM_ELEMS; i++) {")
  main_lines.append("pthread_mutex_init(locks_A + i, NULL);")
  main_lines.append("pthread_mutex_init(locks_Ar + i, NULL);")
  main_lines.append("pthread_mutex_init(locks_Aw + i, NULL);")
  main_lines.append("pthread_mutex_init(locks_Anp + i, NULL);")
  main_lines.append("pthread_mutex_init(locks_Anx + i, NULL);")
  main_lines.append("}")
  main_lines.append("int return_value;")
  main_lines.append("int num_iter_per_thread = NUM_ITER / NUM_THREADS;")
  main_lines.append("for (int i = 0; i < NUM_THREADS; ++i){")
  main_lines.append("struct ThreadArgs *threadArgs = (struct ThreadArgs *)malloc(sizeof(struct ThreadArgs));")
  main_lines.extend(["threadArgs->arg1 = i * num_iter_per_thread;", "if (i != NUM_THREADS - 1)", " threadArgs->arg2 = i * num_iter_per_thread + num_iter_per_thread;"])
  main_lines.extend(["else", "threadArgs->arg2 = NUM_ELEMS;"])
  main_lines.append("if ((return_value = pthread_create(&thread[i], NULL, thread_func, (void *)threadArgs))) {")
  main_lines.append('fprintf(stderr, "error: pthread_create, error code: %d", return_value); return EXIT_FAILURE;}')
  main_lines.append("}")
  main_lines.append(" for (int i = 0; i < NUM_THREADS; ++i) {pthread_join(thread[i], NULL);}")
  main_lines.append('for (int i = 0; i < NUM_ELEMS; ++i) {printf("%d ", A[i]);} printf("\\n"); ')
  main_lines.append('for (int i = 0; i < NUM_ELEMS; i++) {printf("%d ", Aw[i]);} printf("\\n"); ')
  main_lines.append('for (int i = 0; i < NUM_ELEMS; i++) { printf("%d ", Ar[i]);}printf("\\n");for (int i = 0; i < NUM_ELEMS; i++) {printf("%d ", Anx[i]);}printf("\\n");for (int i = 0; i < NUM_ELEMS; i++) {printf("%d ", Anp[i]);}')
  main_lines.append('printf("\\n");')
  main_lines.append('for (int i = 0; i < NUM_ELEMS; ++i){if (Aw[i] == 1) ++distinct_write_counter;}')
  main_lines.append('printf("%d ", write_counter);printf("\\n"); printf("%d ", distinct_write_counter);')
  main_lines.append("return EXIT_SUCCESS;}")

  # major_for_line
  # locked_for_lines
  # thread_func_lines
  # main_lines
  new_lines.extend(main_lines)

  # Extract the filename from the file path
  filename_with_extension = os.path.basename(file_path)

  # Remove the file extension
  filename_without_extension = os.path.splitext(filename_with_extension)[0]
  file_output_path = "./marked_examples/" + filename_without_extension + "_pthreads.c"

  # Open the file for writing
  with open(file_output_path, "w") as file:
      # Iterate through the list and write each line to the file
      for line in new_lines:
          file.write(line + "\n")

  print("Successfully write to: " + file_output_path + "!!!!")

if __name__ == "__main__":
  # Get the current working directory
  current_directory = os.getcwd()
  file_path = sys.argv[1]

  print("Current working directory:", current_directory)
  # file_path = "./marked_examples/marked_simple_500_iter.c"
  num_threads = sys.argv[2]
  convert_serial_to_pthreads(file_path, num_threads)
