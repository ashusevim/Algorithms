#include<bits/stdc++.h>
using namespace std;

int queen[20];  // queen[row] = col, col of a particular row we placed a queen

int n;

bool check(int row, int col){
	// iterate over previous rows
	// no need to check 
	for(int i = 0; i<row; i++){
		int prevR = i;
		int prevC = queen[i]; // previous queen's column
		// If two cells on a grid lie on the same diagonal,
		// difference in their row indices is exactly equal to the difference in their column indices
		if(prevC == col || abs(prevR-row) == abs(prevC-col)){
			return 0;
		}
	}
	return 1;
}

int solve(int level){ // level -> row at which we are placing the queen
	// base case
	if(level == n){
		return 1;
	}
	// global ans to keep track of ways
	int ans = 0;
	// iterate over choices
	for(int col = 0; col < n; col++){
		// check if the choice is valid or not
		if(check(level, col)){
			// place the queen on the valid choice
			queen[level] = col;
			// explore the options
			ans += solve(level+1);
			// revert placing the queen
			queen[level] = -1;
		}
	}
	return ans;
}

int main(){
	cin >> n;
	memset(queen, -1, sizeof(queen));
	cout << solve(0);
}
