#include<bits/stdc++.h>
#include <cstring>
using namespace std;

int n;

int dp[1001];

// return the number of ways to reach n
int recur(int level){ // level -> stairs we are at currently

	//pruning
	if(level > n)return 0;

	// base case
	if(level == n){ // we reached at the N, therefore answer would be guanranteed
		return 1;
	}

	if(dp[level] != -1){
		return dp[level];
	}

	int ans = 0;
	for(int step = 1; step<=3; step++){
		// check for a valid choice
		if(level+step <= n){
			// we found a valid choice
			int ways = recur(level+step);
			ans += ways;
		}
	}
	dp[level] = ans;
	return ans;
}

int main(){
	cin >> n;
	// fill the dp array with -1 value
	memset(dp, -1, sizeof(dp));
	cout << recur(1);

}
