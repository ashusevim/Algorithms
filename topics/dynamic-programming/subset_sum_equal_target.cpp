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
	int ans = 0;
	if(rec(level+1, left)==1){
		ans = 1;
	}
	else if(rec(level+1, left-x[level])){
		ans = 1;
	}

	// save/return
	return dp[level][left] = ans;
}

void printset(int level, int left){
	if(level == n+1){
		return;
	}

	//find the correct transition
	if(rec(level+1, left) == 1){ // don't take
		printset(level+1, left);
	}
	else if(rec(level+1, left-x[level]) == 1){ // take
		cout << x[level] << ' ';
		printset(level+1, left-x[level]);
	}
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
		if(rec(0, t)){
			printset(0, t);
		}
		else{
			cout << "no solution";
		}
	}
}
