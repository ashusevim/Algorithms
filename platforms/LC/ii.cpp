#include<bits/stdc++.h>
using namespace std;
int vowelConsonantScore(string s) {
        int consonents = 0;
        int vowels = 0;
        for(char c:s){
            if(isalpha(c) == true){
                if(c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u'){
                    vowels++;
                }
                else{
                    consonents++;
                }
            }
        }
        int score = 0;
        if(consonents <= 0)score = 0;
        else score = floor(vowels/consonents);
        return score;
    }

    int main(){
        string s = "cooear";
        cout << vowelConsonantScore(s);
    }