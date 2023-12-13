int main() {
    int A[300] = {0};
    int i;

    for (i = 0; i < 300; i++) {
        A[i] = A[i] * A[i] + A[i] * 10;
    }

    return 0;
}