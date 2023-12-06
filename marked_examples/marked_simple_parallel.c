#include <stdio.h>

int main()
{
  int A[4] = {1, 2, 3, 4};
  int Aw[4] = {0, 0, 0, 0};
  int Ar[4] = {0, 0, 0, 0};
  int Anp[4] = {0, 0, 0, 0};
  int Anx[4] = {0, 0, 0, 0};
  int write_counter = 0;
  int distinct_write_counter = 0;
  int i;
  #pragma omp parallel for
  for (i = 0; i < 4; i++){
    int Awi[4] = {0, 0, 0, 0};
    A[i] = A[i] + 5;
    if (Awi[i] == 0)
    {
      Ar[i] = 1;
      Anp[i] = 1;
    }
    Aw[i] = 1;
    Awi[i] = 1;
    Ar[i] = 0;
    #pragma omp critical
    {
    write_counter += 1;
    }
  }
  #pragma omp barrier

  
    #pragma omp parallel for
    for (int i = 0; i < 4; ++i){
        if (Aw[i] == 1)
        ++distinct_write_counter;
    }
    #pragma omp barrier

    for (int i = 0; i < 4; i++) {
        printf("%d ", Aw[i]);
    }
    printf("\n");

    for (int i = 0; i < 4; i++) {
        printf("%d ", Ar[i]);
    }
    printf("\n");

    for (int i = 0; i < 4; i++) {
        printf("%d ", Anx[i]);
    }
    printf("\n");

    for (int i = 0; i < 4; i++) {
        printf("%d ", Anp[i]);
    }
    printf("\n");
    
    printf("%d ", write_counter);
    printf("\n");
    printf("%d ", distinct_write_counter);

    return 0;
    
}

