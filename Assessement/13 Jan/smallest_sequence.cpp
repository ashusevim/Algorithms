#include<bits/stdc++.h>
using namespace std;

// we need to find Lexographically smallest k length subsequence
vector<string> allSubSequences;
int level = 0;
int k;
string s;

void generateAll(int level, string curr){
    // pruning
    
    // base case
    if(level == s.size()){
        if(curr.size() == k) allSubSequences.push_back(curr);
        return;
    }

    // compute
    generateAll(level+1, curr); // not take
    generateAll(level+1, curr+s[level]); // take

    // save/return
}

string subseq(){
    generateAll(0, "");
    sort(allSubSequences.begin(),  allSubSequences.end());
    return allSubSequences[0];
}

int main(){
    cin >> s;
    cin >> k;
    cout << subseq();
}