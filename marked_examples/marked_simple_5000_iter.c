int main()
{
  int A[5000] = {0};
  int Aw[5000] = {0};
  int Ar[5000] = {0};
  int Anp[5000] ={0};
  int Anx[5000] = {0};
  int write_counter = 0;
  int distinct_write_counter = 0;
  int i;
  for (i = 0; i < 5000; i++){
    int Awi[5000] = {0};
    A[i] = A[i] + 5;
    if (Awi[i] == 0)
    {
      Ar[i] = 1;
      Anp[i] = 1;
    }
    Aw[i] = 1;
    Awi[i] = 1;
    Ar[i] = 0;
    write_counter += 1;
  }

  
    for (int i = 0; i < 5000; ++i){
        if (Aw[i] == 1) ++distinct_write_counter;
    }

    for (int i = 0; i < 5000; i++) {
        printf("%d ", Aw[i]);
    }
    printf("\n");

    for (int i = 0; i < 5000; i++) {
        printf("%d ", Ar[i]);
    }
    printf("\n");

    for (int i = 0; i < 1000; i++) {
        printf("%d ", Anx[i]);
    }
    printf("\n");

    for (int i = 0; i < 5000; i++) {
        printf("%d ", Anp[i]);
    }
    printf("\n");

    printf("%d ", write_counter);
    printf("\n");
    printf("%d ", distinct_write_counter);

    return 0;
    
}

