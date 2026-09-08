// A fresh verification of ALL distinct positive quadruples up to a supplied bound.
// No relation-plane list, old enumeration code, or maximum-time lemma is used.
// Reduced rational times provide lower-bound witnesses only. Uncovered inputs are
// decided by exact intersection of the four complete lists of safe intervals.
// C++17. All checks are runtime checks and remain enabled with NDEBUG.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <set>
#include <string>
#include <vector>
using I=std::int64_t;
using V=std::array<int,4>;
struct Rat {I p,q;};
bool less(Rat a,Rat b){return a.p*b.q<b.p*a.q;}
bool safe(int v,Rat t){I r=(I(v)*t.p)%t.q;return 4*r>=t.q && 4*r<=3*t.q;}
bool additive(V v){for(int i=0;i<4;++i)for(int j=i+1;j<4;++j)for(int k=j+1;k<4;++k)if(v[i]+v[j]==v[k])return true;return false;}
// The j-th closed safe interval for speed v is [(4j+1)/(4v),(4j+3)/(4v)].
// By t -> 1-t symmetry only t in [0,1/2] is needed.
bool intersect_intervals(V v,Rat& witness){
    std::array<int,4> j{};
    while(true){
        std::array<Rat,4> lo,hi;
        for(int i=0;i<4;++i){lo[i]={4*I(j[i])+1,4*I(v[i])};hi[i]={4*I(j[i])+3,4*I(v[i])};}
        Rat L=lo[0],U=hi[0];int first_end=0;
        for(int i=1;i<4;++i){if(less(L,lo[i]))L=lo[i];if(less(hi[i],U)){U=hi[i];first_end=i;}}
        if(less({1,2},L))return false;
        if(!less(U,L)){
            for(int speed:v)if(!safe(speed,L))throw std::runtime_error("invalid interval witness");
            witness=L;return true;
        }
        ++j[first_end];
    }
}

int check_additive_branch(){
    constexpr int maxv=445;
    std::vector<Rat> times;
    for(int q=2;q<=31;++q)for(int p=1;2*p<=q;++p)if(std::gcd(p,q)==1)times.push_back({p,q});
    int words=static_cast<int>((times.size()+63)/64);
    std::vector<std::vector<std::uint64_t>> mask(maxv+1,std::vector<std::uint64_t>(words));
    for(int v=1;v<=maxv;++v)for(std::size_t j=0;j<times.size();++j)if(safe(v,times[j]))mask[v][j/64]|=std::uint64_t(1)<<(j%64);
    I total=0,grid_hits=0,interval_hits=0,families=0,isolated=0;
    std::set<V> near;
    for(int a=1;a<108;++a)for(int b=a+1;b<=108;++b){
        if(std::gcd(a,b)!=1 || (a==1&&b==2))continue;
        for(int c=1;c<2*(a+b)+16;++c){
            if(c==a||c==b||c==a+b)continue;
            ++total;V v={a,b,a+b,c};std::sort(v.begin(),v.end());
            Rat t{};bool hit=false;
            for(int w=0;w<words;++w){auto h=mask[v[0]][w]&mask[v[1]][w]&mask[v[2]][w]&mask[v[3]][w];
                if(h){t=times.at(64*w+__builtin_ctzll(h));hit=true;++grid_hits;break;}}
            if(!hit && intersect_intervals(v,t)){hit=true;++interval_hits;}
            if(hit){for(int speed:v)if(!safe(speed,t))throw std::runtime_error("additive witness check");continue;}
            near.insert(v);
            bool family=(v[0]+v[1]==v[2]) && (v[3]-v[2]==v[0] || v[3]-v[2]==v[1]);
            if(family){++families;continue;}
            if(v==V{1,3,4,14}){++isolated;continue;}
            std::cerr<<"UNCLASSIFIED_ADDITIVE ";for(int x:v)std::cerr<<x<<' ';std::cerr<<'\n';return 2;
        }
    }
    if(total!=815970 || families!=7148 || isolated!=1 || near.size()!=4771 || total!=grid_hits+interval_hits+families+isolated)throw std::runtime_error("additive coverage count mismatch");
    std::cout<<"{\n  \"status\":\"PASS\",\n  \"parameter_triples\":"<<total
    <<",\n  \"rational_grid_witnesses\":"<<grid_hits
    <<",\n  \"exact_interval_safe_witnesses\":"<<interval_hits
    <<",\n  \"exact_interval_near_tight\":"<<families+isolated
    <<",\n  \"U2_parameter_triples\":"<<families
    <<",\n  \"isolated_parameter_triples\":"<<isolated
    <<",\n  \"distinct_near_tight_speed_sets\":"<<near.size()
    <<",\n  \"unclassified\":0,\n  \"method\":\"exact intersection of safe intervals; no pair-sum candidate lemma\"\n}\n";
    return 0;
}

int main(int argc,char**argv){try{
    if(argc>1 && std::string(argv[1])=="additive")return check_additive_branch();
    int n=argc>1?std::stoi(argv[1]):290;
    int grid=argc>2?std::stoi(argv[2]):31;
    if(n<4||n>10000||grid<0||grid>200)throw std::runtime_error("bounds out of audited arithmetic range");
    std::vector<Rat> times;
    for(int q=2;q<=grid;++q)for(int p=1;2*p<=q;++p)if(std::gcd(p,q)==1)times.push_back({p,q});
    const int words=static_cast<int>((times.size()+63)/64);
    std::vector<std::vector<std::uint64_t>> m(n+1,std::vector<std::uint64_t>(words));
    for(int v=1;v<=n;++v)for(std::size_t j=0;j<times.size();++j)if(safe(v,times[j]))m[v][j/64]|=std::uint64_t(1)<<(j%64);
    I total=0,excluded=0,checked=0,grid_hits=0,interval_hits=0;
    std::uint64_t checksum=1469598103934665603ULL;
    auto absorb=[&](I x){checksum^=std::uint64_t(x);checksum*=1099511628211ULL;};
    std::vector<std::uint64_t> triple(words);
    for(int a=1;a<=n-3;++a)for(int b=a+1;b<=n-2;++b)for(int c=b+1;c<=n-1;++c){
        for(int w=0;w<words;++w)triple[w]=m[a][w]&m[b][w]&m[c][w];
        for(int d=c+1;d<=n;++d){
            ++total;V v={a,b,c,d};
            if(additive(v)){++excluded;continue;}
            ++checked;bool hit=false;Rat t{};
            for(int w=0;w<words;++w){auto h=triple[w]&m[d][w];if(h){
                auto k=64*w+__builtin_ctzll(h);t=times.at(k);hit=true;++grid_hits;break;
            }}
            if(!hit){if(!intersect_intervals(v,t)){
                std::cerr<<"UNSAFE_INPUT "<<a<<' '<<b<<' '<<c<<' '<<d<<'\n';return 2;}
                ++interval_hits;
            }
            for(int speed:v)if(!safe(speed,t))throw std::runtime_error("witness recheck failed");
            for(int speed:v) { absorb(speed); }
            absorb(t.p); absorb(t.q);
        }
    }
    I expected=I(n)*(n-1)*(n-2)*(n-3)/24;
    if(total!=expected || total!=excluded+checked || checked!=grid_hits+interval_hits)throw std::runtime_error("loop coverage check failed");
    std::cout<<"{\n  \"status\":\"PASS\",\n  \"maximum_speed\":"<<n
    <<",\n  \"all_distinct_positive_quadruples\":"<<total
    <<",\n  \"excluded_additive_quadruples\":"<<excluded
    <<",\n  \"nonadditive_quadruples_all_scales\":"<<checked
    <<",\n  \"rational_grid_witnesses\":"<<grid_hits
    <<",\n  \"exact_interval_witnesses\":"<<interval_hits
    <<",\n  \"grid_denominator_bound\":"<<grid
    <<",\n  \"grid_size\":"<<times.size()
    <<",\n  \"witness_stream_fnv64\":\""<<checksum<<"\",\n  \"uncovered\":0\n}\n";
}catch(const std::exception&e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 1;}}
