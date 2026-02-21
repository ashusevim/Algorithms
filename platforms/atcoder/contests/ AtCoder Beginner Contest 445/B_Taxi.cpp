#include<bits/stdc++.h>
using namespace std;

int main(){
    int n;
    cin >> n;
    vector<int> v(5, 0);
    for(int i = 0; i<n; i++){
        int x;
        cin >> x;
        v[x]++;
    }
    int final = v[4];
    if(v[3] <= v[1]){
        final += v[3];
        v[1] -= v[3];
    }
    else{
        v[1] = 0;
        final += v[3];
    }

    while(v[2] > 0){
        // 2 ones with 1 two -> total 4 childrens
        if(v[1] > 0){
            v[2]--;
            v[1]=v[1]-2;
            final++;
        }
        else{
            v[2]=v[2]-2;
            final++;
        }
    }

    while(v[1] > 0){
        v[1]=v[1]-4;
        final++;
    }

    cout << final << '\n';
}