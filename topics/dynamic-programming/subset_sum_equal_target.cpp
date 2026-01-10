// dp with caching across querie
#include<bits/stdc++.h>
using namespace std;

int n;
int t;
int x[101];

int dp[101][1001];

int rec(int level, int left){
	// pruning
	if(left < 0)return 0;

	// base case
	if(level == n){
		if(left == 0)return 1;
		else return 0;
	}

	// cache check
	if(dp[level][left] != -1){
		return dp[level][left];
	}

	// compute/transation
	int ans = rec(level+1, left);
	if(left-x[level] >= 0){
		ans = rec(level+1, left-x[level]);
	}

	// save/return
	return dp[level][left] = ans;
}

int main(){
	cin >> n;
	for(int i = 0; i<n; i++){
		cin >> x[i];
	}
	int q;
	cin >> q;
	memset(dp, -1, sizeof(dp));
	while(q--){
		cin >> t;
		cout << rec(0, t);
	}
}
