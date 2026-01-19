#include <bits/stdc++.h>
using namespace std;

typedef long long ll;

int main() {
    ll t;
    cin >> t;  // Uncomment for multiple test cases
    
    while (t--) {
        ll n, operations, maxCanStore;
        cin >> n >> operations >> maxCanStore;
        vector<ll> v;
        vector<ll> ans;
        for(ll i = 0; i<n; i++){
            ll x;
            cin >> x;
            v.push_back(x);
            ans.push_back(x);
        }

        vector<pair<int, int>> p;
        for(ll i = 0; i<operations; i++){
            ll b, c;
            cin >> b >> c;
            ans[b-1] = ans[b-1] + c;
            p.push_back({b-1, c});
            if(ans[b-1] > maxCanStore){
                for(auto pair:p){
                    ll x = pair.first;
                    ans[x] -= pair.second;
                }   
                p.clear();
            }
        }       
        for(auto i:ans){
            cout << i << " ";
        }
        cout << '\n';
    }
    
    return 0;
}