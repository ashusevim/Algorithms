#include<bits/stdc++.h>
using namespace std;

#define ll long long

int main(){
    ll t;
    cin >> t;
    while(t--){
        ll n;
        cin >> n;
        if(n % 2 != 0 || n < 4)cout << -1 << '\n';
        else{
            cout << ((n+5)/6) << " " << n/4 << '\n';
        } 
    }
}