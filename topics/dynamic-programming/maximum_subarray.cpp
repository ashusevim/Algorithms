#include<bits/stdc++.h>
using namespace std;

int dp[101][101];
int rec(int level, int n, int sum, vector<int> v){
    
    // pruning

    // base case
    if(level == n)return sum;

    // cache check

    // computing/transition
    int current = 0;
    current = max(current, rec(level+1, n, sum, v));
    if(sum+v[level+1] < 0){
        current = max(current, rec(level+1, n, sum+sum+v[level+1], v));
    }

    // save/return
    return current;
}

int main(){
    int n;
    cin >> n;
    vector<int> v;
    for(int i = 0; i<n; i++){
        int x;cin >> x;
        v.push_back(x);
    }
    memset(dp, -1, sizeof(dp));
    cout << rec(0, n-1, 0, v);
}