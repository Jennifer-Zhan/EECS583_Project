int main()
{
  int A[4] = {1, 2, 3, 4};
  int Aw[4] = {0, 0, 0, 0};
  int Ar[4] = {0, 0, 0, 0};
  int Anp[4] = {0, 0, 0, 0};
  int Anx[4] = {0, 0, 0, 0};
  int write_counter = 0;
  int distinct_write_counter = 0;
  int B[4] = {0, 0, 1, 1};
  int K[4] = {1, 3, 3, 1};
  int L[4] = {2, 2, 3, 3};
  int R[4] = {4, 4, 4, 4};
  int i;
  for (i = 0; i < 4; i++)
  {
    int Awi[4] = {0, 0, 0, 0};
    int z = A[K[i]];
    if (Awi[K[i]] == 0)
    {
      Ar[K[i]] = 1;
      Anp[K[i]] = 1;
    }
    Anx[K[i]] = 1;
    if (B[i] == 0)
    {
      A[L[i]] = z + 5;
      A[R[i]] = A[R[i]] + 1;
      Aw[L[i]] = 1;
      Awi[L[i]] = 1;
      Ar[L[i]] = 0;
      write_counter += 1;
      Anx[L[i]] = 1;
      if (Awi[R[i]] == 0)
      {
        Ar[R[i]] = 1;
        Anp[R[i]] = 1;
      }
      Aw[R[i]] = 1;
      Awi[R[i]] = 1;
      Ar[R[i]] = 0;
      write_counter += 1;
    }
  }

  
    for (int i = 0; i < 4; ++i){
        if (Aw[i] == 1)
        ++distinct_write_counter;
    }

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

