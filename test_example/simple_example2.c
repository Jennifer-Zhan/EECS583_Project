int main() {
    int A[4] = {1, 2, 3, 4};
    for(int i=0; i<4; ++i){
        A[i] = i+1;
    }
    for(int i=0; i<4; ++i){
        A[i] = A[i]+1;
    }
    for(int i=0; i<4; ++i){
        cout<<A[i]<<" ";
    }
}