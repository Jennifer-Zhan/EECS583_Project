int main() {
    int A[500] = {0};
    int i;

    for (i = 0; i < 500; i++) {
        A[i] = A[i] * A[i] + A[i] * 10;
    }

    return 0;
}