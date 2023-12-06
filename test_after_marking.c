#include <stdio.h>
#include <string.h>

int main()
{
  int A[4] = {1, 2, 3, 4};
  int Aw[4] = {0, 0, 0, 0};
  int Ar[4] = {0, 0, 0, 0};
  int Anp[4] = {0, 0, 0, 0};
  int Anx[4] = {0, 0, 0, 0};
  int Awi[4] = {0, 0, 0, 0};
  int write_counter = 0;
  int i;
  for (i = 0; i < 4; i++){
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
    memset(Awi, 0, sizeof(Awi));
  }
  for (i = 0; i < 4; i++){
    printf("%d %d %d %d %d %d\n", A[i], Aw[i], Ar[i], Anp[i], Anx[i], Awi[i]);
  }

  return 0;
}