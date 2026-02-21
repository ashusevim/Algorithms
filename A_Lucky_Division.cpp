#include<bits/stdc++.h>
using namespace std;

int main(){
    int n;
    cin >> n;
    string str = to_string(n);
    int cnt = 0;
    for(char c:str){
        if(c == '4' || c == '7')continue;
        else{
            cnt++;
            break;
        }
    }
    // cout << n % 47 << " " << n % 74 << '\n';
    if(cnt == 0){
        cout << "YES" << '\n';
    }
    else if(cnt>=0 && n % 4 == 0 || n % 7 == 0 || n % 47 == 0 || n % 74 == 0){
        cout << "YES" << '\n';
    }
    else{
        cout << "NO" << '\n';
    }
}