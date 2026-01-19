#include<bits/stdc++.h>
using namespace std;

int isPalindrome(string& s){
    int left = 0, right = s.size()-1;
    while(left < right){
        if(tolower(s[left]) != tolower(s[right])){
            return 0;
        }
        else{
            left++;
            right--;
        }
    }
    return 1;
}

int main(){
    string s = "is this paap siht s";
    cout << isPalindrome(s);
}