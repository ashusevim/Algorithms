#include<bits/stdc++.h>
using namespace std;

int maxCapacity(vector<int>& costs, vector<int>& capacity, int budget) {
    int n = costs.size();
    vector<pair<int,int>> p(n);
    for(int i = 0; i<costs.size(); i++) p[i] = make_pair(costs[i], capacity[i]);
    sort(p.begin(), p.end());
    for(int i = 0; i<n; i++){
        costs[i] = p[i].first;
        capacity[i] = p[i].second;
    }

    int prefix[n];
    prefix[0] = capacity[0];
    for(int i = 1; i<costs.size(); i++){
        prefix[i] = max(prefix[i-1], capacity[i]);
    }
    
    int ans = 0;
    // choosing one machine
    for(int i = 0; i<n; i++){
        if(costs[i] < budget) ans = max(ans, prefix[i]);
    }

    // choosing two machines
    for(int i = 1; i<n; i++){
        int limit = budget - costs[i];
        if(limit <= 0)continue;
        int left = 0, right = i-1;
        int idx = -1;
        while(left <= right){
            int mid = left + (right-left)/2;
            if(costs[mid] < limit){
                idx = mid;
                left = mid+1;
            }
            else{
                right = mid-1;
            }

        }
        // cout << idx << " ";
        // cout << '\n';
        if(idx != -1){
            ans = max(ans, capacity[i] + prefix[idx]);
        }
    }

    return ans;
}

int main(){
    int n;
    cin >> n;
    int budget;
    vector<int> costs(n);
    vector<int> capacity(n);
    for(int i = 0; i<n; i++)cin >> costs[i];
    for(int i = 0; i<n; i++)cin >> capacity[i];
    cin >> budget;
    cout << maxCapacity(costs, capacity, budget);
}
