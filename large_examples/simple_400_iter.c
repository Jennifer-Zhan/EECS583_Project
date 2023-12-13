int main() {
    int A[400] = {0};
    int i;

    for (i = 0; i < 400; i++) {
        A[i] = A[i] * A[i] + A[i] * 10;
    }

    return 0;
}