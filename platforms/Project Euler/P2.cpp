#include<iostream>
using namespace std;

int main(){
    long long dp[1000001];
    dp[0] = 0;
    dp[1] = 1;
    long long sum = 0;
    for(int i = 2; ;i++){
        dp[i] = dp[i-1] + dp[i-2];
        if(dp[i] >= 4000000){
            break;
        }
        if(i % 2 == 0){
            sum += dp[i];
        }
    }
    cout << sum << '\n';
}
