int main() {
    int A[4] = {1, 2, 3, 4};
    #pragma omp parallel for
    for(int i=0; i<4; ++i){
        A[i] = i+1;
    }
    #pragma omp barrier
}