#include<bits/stdc++.h>
using namespace std;
// for(int i = 0; i<n; i++){
//     if(i%2==0){
//         for(int x = 0; x<m; x++)cout << "#";
//     }
//     else{
//         if(!lToR){
//             for(int x = 0; x<m-1; x++)cout << '.';
//             cout << "#"; 
//         }
//         else{
//             cout << "#";
//             for(int x = 1; x<m; x++)cout << '.';
//         }
//         lToR = !lToR;
        
//     }
//     cout << '\n';
// }

int n, m;
int t = 1;
bool lToR = false;

int main(){
    while(t--){
        cin >> n >> m;
        for(int i = 1; i<=n; i++){
            for(int j = 1; j<=m; j++){
                bool haveSnake = false;
                if(i % 2 == 1){
                    haveSnake = true;
                }
                else{
                    if(i % 4 == 2){
                        haveSnake = (j == m);
                    }
                    if(i % 4 == 0){
                        haveSnake = (j == 1);
                    }
                }
                cout << (haveSnake ? "#" : ".");
            }
            cout << '\n';
        }
    }
}