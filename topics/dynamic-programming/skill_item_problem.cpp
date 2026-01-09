/* problem statement: you have N problems/items where the i-th item takes Ti time and gives Si skill points
You have a maximum time limit of X and can select at most K items.
The goal is to maximize the total skill gained */
#include<bits/stdc++.h>
using namespace std;

int n;
int t[1001];
int s[1001];
int x, k; // limits

int recur(int level, int time_taken, int item_taken){
	// pruning

	// base case
	if(level == n){
		return 0;
	}

	// cache check

	// compute/transition
	int ans = recur(level+1, time_taken, item_taken);
	if(time_taken+t[level] <= x && item_taken+1 <= k){
		ans = max(ans, s[level] + recur(level+1, time_taken+t[level], item_taken+1));
	}

	// save/return
}

int main(){
	cin >> n;
	for(int i = 0; i<n; i++){
		cin >> t[i] >> s[i];
	}
	cin >> x >> k;
	cout << recur(0);
}
