#include<bits/stdc++.h>
using  namespace std;

int n;
int arr[10001];
int dp[10001];

int rec(int level){
    // pruning
    if(level < 0)return 0;

    // base case

    // cache check
    if(dp[level] != -1)return dp[level];

    // computing/transition
    int ans = 1;
    for(int prev_taken = 0; prev_taken<level; prev_taken++){
        if(arr[prev_taken] < arr[level]){
            ans = max(ans, 1+rec(prev_taken));
        }
    }

    // save/return
    return dp[level] = ans;
}

int main(){
    cin >> n;
    for(int i = 0; i<n; i++){
        cin >> arr[i];
    }
    memset(dp, -1, sizeof(dp));
    int best = 0;
    for(int i = 0; i<n; i++){
        best = max(best, rec(i));
    }
}