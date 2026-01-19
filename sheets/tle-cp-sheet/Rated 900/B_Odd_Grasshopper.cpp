#include<bits/stdc++.h>
using namespace std;

int main(){
    long long test;
    cin >> test;
    while(test--){
        long long x, n;
        cin >> x >> n;
        // n-(n%4) -> the number of steps that do form complete blocks
        for(long long i = n-n%4+1; i<=n; i++){
            // cout << i << " ";
            if(x%2==0){
                x=x-i;
            }
            else{
                x=x+i;
            }
        }
        // cout << '\n';
        cout << x << '\n';

    }
}