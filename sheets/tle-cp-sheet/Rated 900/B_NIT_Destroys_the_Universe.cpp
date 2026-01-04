#include<bits/stdc++.h>
using namespace std;

#define ll long long

int main(){
    ll test;
    cin >> test;
    while(test--){
        ll n;
        cin >> n;
        vector<ll> v(n);
        for(int i = 0; i<n; i++)cin >> v[i];
        ll cnt = 0, flag = 0;
        for(int i = 0; i<n; i++){
            if(v[i] == 0){
                flag = 0;
            }
            else if(v[i] != 0 && flag == 0){
                cnt++;
                flag = 1;
            }
        }
        if(cnt >= 2){
            cout << 2 << '\n';
        }
        else cout << cnt << '\n';
        // cout << cnt << '\n';
    }
}