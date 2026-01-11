#include<bits/stdc++.h>
using namespace std;

/*
    sol: 
    string s;
        cin >> s;
        int digits = 1;
        int non = 0;
        for(char c:s)if(c!='0')non++;
        cout << non << '\n';
        for(int i = s.size()-1; i>=0; i--){
            if(s[i] == '0'){
                digits++;
                continue;
            }
            cout << s[i];
            for(int x = 0; x<digits-1; x++){
                cout << '0';
            }
            digits++;
            cout << " ";
        }
        cout << '\n';
*/

int main(){
    int t;
    cin >> t;
    while(t--){
        int n;
        cin >> n;
        vector<int> ans;
        int power = 1;
        while(n > 0){
            int digit = n%10;
            if(digit != 0){
                ans.push_back(digit*power);
            }
            n = n/10;
            power = power * 10;
        }
        cout << ans.size() << '\n';
        for(auto i:ans)cout << i << " ";
        cout << '\n';
    }
}