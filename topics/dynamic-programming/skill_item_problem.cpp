/* problem statement: you have N problems/items where the i-th item takes Ti time and gives Si skill points
You have a maximum time limit of X and can select at most K items.
The goal is to maximize the total skill gained */
#include<bits/stdc++.h>
using namespace std;

int n;
int t[1001];
int s[1001];
int x, k; // limits

int taken[1001];

bool check(int level){
	int timetaken = 0;
	int itemtaken = 0;
	for(int i = 0; i<level; i++){
		if(taken[i]){
			timetaken += t[i];
			itemtaken += 1;
		}
	}
	// take the current item
	timetaken += t[level];
	itemtaken++;

	if(timetaken <= x && itemtaken <= k){
		return 1;
	}
	else{
		return 0;
	}
}

int recur(int level){
	// base case
	if(level == n)return 0;

	// compute
	// look over choices
	// choice 1: not take
	int ans = recur(level+1);
	// choice 2: take
	// validate the choice
	if(check(level)){
		taken[level] = 1;
		ans = max(ans, s[level]+recur(level+1));
		taken[level] = 0;
	}
	return ans;
}

int main(){
	cin >> n;
	for(int i = 0; i<n; i++){
		cin >> t[i] >> s[i];
	}
	cin >> x >> k;
	cout << recur(0);
}
