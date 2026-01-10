#include<bits/stdc++.h>
using namespace std;

int n;
int t;
int x[101];

int dp[101][101];

int rec(int level, int sum){
	// pruning
	if(sum > t)return 0;

	// base case
	if(level == n){
		if(sum == t)return 1;
		else return 0;
	}

	// cache check
	if(dp[level][sum] != -1){
		return dp[level][sum];
	}

	// compute/transation
	int ans = rec(level+1, sum);
	if(sum+x[level] <= t){
		ans = rec(level+1, sum+x[level]);
	}

	// save/return
	return dp[level][sum] = ans;
}

int main(){
	cin >> n;
	for(int i = 0; i<n; i++){
		cin >> x[i];
	}
	cin >> t;
	memset(dp, -1, sizeof(dp));
	cout << rec(0, 0);
}
