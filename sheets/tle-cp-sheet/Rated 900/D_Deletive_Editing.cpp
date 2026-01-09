#include<bits/stdc++.h>
using namespace std;

#define ll long long
vector<char>cnt(26, 0), cnt2(26, 0);

int main(){
    int t;
    cin >> t;
    while(t--){
        string s, t;
        cin >> s >> t;
        vector<int> cnt(257);
        for(int i = 0; i<t.size(); i++){
            cnt[t[i]]++;
        }
        string g = "";
        for(int i = s.size()-1; i>=0; i--){
            if(cnt[s[i]] > 0){
                g += s[i];
                cnt[s[i]]--;
            }
        }
        reverse(g.begin(), g.end());
        if(g == t)cout << "YES" << '\n';
        else cout << "NO" << '\n';
    }
}