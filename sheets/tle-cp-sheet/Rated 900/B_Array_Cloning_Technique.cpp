#include<bits/stdc++.h>
using namespace std;

int main(){
    int t;
    cin >> t;
    while(t--){
        int n;
        cin >> n;
        unordered_map<int, int> mp;
        for(int i = 0; i<n; i++){
            int x;
            cin >> x;
            mp[x]++;
        }
        int am = 0;
        for(auto& [x, y]: mp){
            am = max(am, y);
        }

        int ans = 0;
        while(am < n){
            int d = min(n-am, am);
            ans += d+1; //after putting all most common am elements and +1 for cloning the array
            am += d;
        }
        cout << ans << '\n';
    }
}