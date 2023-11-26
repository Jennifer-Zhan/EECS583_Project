int main()
{
  int A[4] = {1, 2, 3, 4};
  int B[4] = {0, 0, 1, 1};
  int K[4] = {1, 3, 3, 1};
  int L[4] = {2, 2, 3, 3};
  int R[4] = {4, 4, 4, 4};
  int i;
  for (i = 0; i < 4; i++)
  {
    int z = A[K[i]];
    if (B[i] == 0)
    {
      A[L[i]] = z + 5;
      A[R[i]] = A[R[i]] + 1;
    }
  }

  return 0;
}

int A_copy[4] = {0, 0, 0, 0};

