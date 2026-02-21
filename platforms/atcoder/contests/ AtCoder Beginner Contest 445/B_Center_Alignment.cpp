#include <bits/stdc++.h>
using namespace std;

int main()
{
    int test;
    cin >> test;
    vector<string> vc;
    int maximumLength = 0;
    while(test--){
        string s;
        cin >> s;
        maximumLength = max(maximumLength, (int)s.size());
        vc.push_back(s);
    }
    vector<int> dots;
    for(string sc:vc){
        int numberOfDots = maximumLength-sc.size();
        dots.push_back(numberOfDots);
    }
    
    for(int i = 0; i<dots.size(); i++){
        int half = dots[i]/2;
        for(int x = 0; x<half; x++){
            cout << '.';
        }
        cout << vc[i];
        for(int x = 0; x<half; x++){
            cout << '.';
        }
        cout << '\n';
    }
}