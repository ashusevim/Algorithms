#include <bits/stdc++.h>
using namespace std;

typedef long long ll;
typedef vector<int> vi;
typedef vector<ll> vll;
typedef vector<vi> vvi;
typedef vector<vll> vvll;
typedef pair<int, int> pii;
typedef pair<ll, ll> pll;
typedef vector<pii> vpii;
typedef vector<pll> vpll;

// Macros for common operations
#define F first
#define S second
#define PB push_back
#define MP make_pair
#define REP(i, a, b) for (int i = a; i <= b; i++)
#define REPR(i, a, b) for (int i = a; i >= b; i--)
#define all(x) begin(x), end(x)
#define sz(x) (int)(x).size()

// Constants
const int MOD = 1e9 + 7;
const int INF = 1e9;
const ll LLINF = 1e18;
const double EPS = 1e-9;

// Debug template
template<typename T>
void debug(T x) {
    cerr << x << endl;
}

template<typename T, typename... Args>
void debug(T x, Args... args) {
    cerr << x << " ";
    debug(args...);
}

// Fast I/O
void fast_io() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    cout.tie(NULL);
}

// Custom hash for unordered_map/set
struct custom_hash {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
        x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t FIXED_RANDOM = chrono::steady_clock::now().time_since_epoch().count();
        return splitmix64(x + FIXED_RANDOM);
    }
};

class Solution {
public:
    void solve() {
        string s;
        cin >> s;
        int n = s.size();
        int remove = 0;
        int first = -1, last = -1;
        for(int i = s.size()-1; i>=0; i--){
            if(last == -1 && (s[i] == '0' || s[i] == '5')){
                last = 1;
            }
            else if(last == 1 && first == -1 && s[i] == '0' || s[i] == '2' || s[i] == '5' || s[i] == '7'){
                first = 1;
            }
            else{
                remove++;
            }
            if(first == 1 && last == 1){
                break;
            }
        }
        cout << remove << '\n';
    }
};

int main() {
    fast_io();
    
    int t = 1;
    cin >> t;
    
    while (t--) {
        Solution sol;
        sol.solve();
    }
    
    return 0;
}