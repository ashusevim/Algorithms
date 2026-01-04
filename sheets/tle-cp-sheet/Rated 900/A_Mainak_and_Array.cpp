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
        for(int i = 0; i<n; i++){
            cin >> v[i];
        }    
        ll ans = LLONG_MIN;
        for(int i = 0; i<n; i++){
            ans = max(ans, v[(i-1+n)%n] - v[i]);
        }

        for(int i = 1; i<n; i++){
            ans = max(ans, v[i] - v[0]);
        }

        for(int i = 0; i<n-1; i++){
            ans = max(ans, (v[n-1] - v[i]));
        }
        cout << ans << '\n';
    }
}