/*
 * @lc app=leetcode id=3510 lang=cpp
 *
 * [3510] Minimum Pair Removal to Sort Array II
 */

#include<bits/stdc++.h>

// @lc code=start
class Solution {
public:
    int minimumPairRemoval(vector<int>& nums) {
        int n = nums.size();
        vector<long long> temp(n);
        for(int i = 0; i<nums.size(); i++){
            temp[i] = nums[i];
        }

        // pair<sum, index>
        set<pair<long long, int>> minPairSet;

        vector<long long> nextIndex;
        vector<long long> prevIndex;

        for(int i = 0; i<n; i++){
            prevIndex[i] = i-1;
            nextIndex[i] = i+1;
        }

        // find out how many bad pairs present
        int badPair = 0;
        for(int i = 0; i<n-1; i++){
            if(temp[i] > temp[i+1]){
                badPair++;
            }
            minPairSet.insert({temp[i] + temp[i+1], i});
        }

        int operations = 0;
        while(badPair > 0){
            int first = minPairSet.begin()->second;
            int second = nextIndex[first];

            int first_left = prevIndex[first];
            int second_right = nextIndex[second];

            minPairSet.erase(begin(minPairSet));

            if(temp[first] > temp[second]){
                badPair--;
            }

            if(first_left >= 0){
                if(temp[first_left] > temp[first] && temp[first_left] <= temp[first] + temp[second]){
                    badPair--;
                }
                else if(temp[first_left] <= temp[first] && temp[first_left] > temp[first] + temp[second]){
                    badPair++;
                }
            }

            if(second_right < n){
                if(temp[second_right] >= temp[second] && temp[second_right] < temp[first] + temp[second]){
                    badPair++;
                }
                else if(temp[second_right] < temp[second] && temp[second_right] >= temp[first] + temp[second]){
                    badPair--;
                }
            }

            if(first_left >= 0){
                minPairSet.erase({temp[first_left] + temp[first], first_left});
                minPairSet.insert({temp[first_left] + temp[first] + temp[second], first_left});
            }

            if(second_right < n){
                minPairSet.erase({temp[second_right] + temp[second], second_right});
                minPairSet.insert({temp[second_right] + temp[first] + temp[second], second_right});
                prevIndex[second_right] = first;
            }

            nextIndex[first] = second_right;
            temp[first] += temp[second];
            operations++;
        }
        return operations;
    }
};
// @lc code=end#include<bits/stdc++.h>


