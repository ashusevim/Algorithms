#include<bits/stdc++.h>
using namespace std;

#define ll long long

int main(){
    ll t;
    cin >> t;
    while(t--){
        ll a, b, c;
        cin >> a >> b >> c;
        ll newa = b - (c-b);
        if(newa >= a && newa % a == 0 && newa != 0){
            cout << "YES" << '\n';
            continue;
        }

        ll newb = a + (c-a)/2;
        if(newb >= b && (c-a)%2==0 && newb % b == 0 && newb != 0){
            cout << "YES" << '\n';
            continue;
        }

        ll newc = a + 2*(b-a);
        if(newc >= c &&  newc % c == 0 && newc != 0){
            cout << "YES" << '\n';
            continue;
        }

        cout << "NO" << '\n';
        continue;
    }
}