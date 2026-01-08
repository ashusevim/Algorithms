#include<bits/stdc++.h>
using namespace std;

#define ll long long

int main(){
    int t;
    cin >> t;
    while(t--){
        int n;
        cin >> n;
        vector<int> v(n);
        for(int i = 0; i<n; i++)cin >> v[i];
        if(v[0] + v[n-1] == 0)cout << "Bob" << '\n';
        else cout << "Alice" << '\n';
    }
}