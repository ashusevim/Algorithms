#include<bits/stdc++.h>
using namespace std;

int main(){
    int t;
    cin >> t;
    while(t--){
        int n;
        cin >> n;
        if(n==2 || n == 3){
            cout  << n << '\n';
            continue;   
        }
        else{
            cout << (n%2==0 ? 0 : 1) << '\n';
        }
    }
}