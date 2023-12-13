# EECS583_Project - Speculatively Parallelizing DOALL Loops using LRPD Test

Our project aims to parallelize the DOALL loop by speculatively executing the loop in parallel and detecting whether the loop is a DOALL loop through applying the LRPD test.

## How to Use

Testcases: All our large testcases are located under large_examples directory. By executing parse.py, we could mark the testcase and save the marked file under marked_examples. Before running the parse.py, you would need to copy the test file from large_examples directory to project home directory, then execute `python src/parse.py <filename>`.

Then we could run convert_parallel_openmp.py or convert_parallel_pthreads.py under src directory to convert the serial marked code to parallel versions.

The lrpd_test.py would analyze the result after the marking phase and determine if the loop is a DOALL loop.

demo.ipynb includes a demo of the whole process for how we use this program.

## Reference

LRPD Test Paper: https://ieeexplore.ieee.org/document/752782

Pthread Tutorial: https://randu.org/tutorials/threads/

## Contributors

Pranav Bhoopala, Ruoyi Zhan, Yuhao Zhou

## Notes

if you have trouble running the demo.ipynb or convert_parallel_openmp.py, please double check the path for Clang library and set libarary path to the correct path.
