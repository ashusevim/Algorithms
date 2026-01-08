#include<bits/stdc++.h>
using namespace std;

int n;
// return the number of ways to reach n
int solve(int level){ // level -> stairs we are at currently

	//pruning
	if(level > n)return 0;

	// base case
	if(level == n){ // we reached at the N, therefore answer would be guanranteed
		return 1;
	}

	int ans = 0;
	for(int step = 1; step<=3; step++){
		// check for a valid choice
		if(level+step <= n){
			// we found a valid choice
			int ways = solve(level+step);
			ans += ways;
		}
	}
	return ans;
}

int main(){
	cin >> n;
	cout << solve(1);
}
