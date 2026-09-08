// Generate reduced saturated speed-plane bases and exact safe-point certificates
// from canonical primitive relation-plane Pluecker tuples.
// C++17; no floating point is used in theorem-deciding comparisons.
#include <array>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using I = std::int64_t;
using V4 = std::array<I,4>;
using P6 = std::array<I,6>;
constexpr std::array<std::pair<int,int>,6> EDGES={{{0,1},{0,2},{0,3},{1,2},{1,3},{2,3}}};
I igcd(I a,I b){return std::gcd(a,b);} I gcd6(P6 p){I g=0;for(I x:p)g=igcd(g,std::llabs(x));return g;}
I gcd_minors(const V4&u,const V4&w){I g=0;for(auto [i,j]:EDGES)g=igcd(g,std::llabs(u[i]*w[j]-u[j]*w[i]));return g;}
P6 minors(const V4&u,const V4&w){P6 p{};int k=0;for(auto [i,j]:EDGES)p[k++]=u[i]*w[j]-u[j]*w[i];return p;}
P6 primitive(P6 p){I g=gcd6(p);if(!g)return p;I first=0;for(I x:p)if(x){first=x;break;}if(first<0)g=-g;for(I&x:p)x/=g;return p;}
P6 hodge(P6 p){return primitive(P6{p[5],-p[4],p[3],p[2],-p[1],p[0]});}
I Q(const P6&q,int i,int j){if(i>j)return -Q(q,j,i);for(int k=0;k<6;++k)if(EDGES[k]==std::pair<int,int>{i,j})return q[k];throw std::runtime_error("bad edge");}
I prime_factor(I n){n=std::llabs(n);if(n%2==0)return 2;for(I p=3;p*p<=n;p+=2)if(n%p==0)return p;return n;}
I mod(I x,I p){x%=p;if(x<0)x+=p;return x;}
I invmod(I a,I p){I t=0,newt=1,r=p,newr=mod(a,p);while(newr){I q=r/newr;I z=t-q*newt;t=newt;newt=z;z=r-q*newr;r=newr;newr=z;}if(r!=1)throw std::runtime_error("inverse");return mod(t,p);}
void saturate(V4&u,V4&w){while(true){I d=gcd_minors(u,w);if(d==1)return;I p=prime_factor(d);bool uz=true,wz=true;for(int i=0;i<4;++i){uz&=(mod(u[i],p)==0);wz&=(mod(w[i],p)==0);}if(uz){for(I&x:u)x/=p;continue;}if(wz){for(I&x:w)x/=p;continue;}int idx=0;while(idx<4&&mod(u[idx],p)==0)++idx;if(idx==4)throw std::runtime_error("saturation rank");I c=mod(w[idx]*invmod(u[idx],p),p);for(int i=0;i<4;++i)if(mod(w[i]-c*u[i],p)!=0)throw std::runtime_error("saturation dependency");for(int i=0;i<4;++i)w[i]=(w[i]-c*u[i])/p;}}
std::pair<V4,V4> basis_from_relation_pluecker(P6 p){P6 q=hodge(p);int a=-1,b=-1;for(auto [i,j]:EDGES)if(Q(q,i,j)){a=i;b=j;break;}if(a<0)throw std::runtime_error("zero pluecker");I qab=Q(q,a,b);V4 u{},w{};u[a]=qab;w[b]=qab;for(int k=0;k<4;++k)if(k!=a&&k!=b){w[k]=Q(q,a,k);u[k]=-Q(q,b,k);}P6 got=minors(u,w);for(int k=0;k<6;++k)if(got[k]!=qab*q[k])throw std::runtime_error("basis construction");saturate(u,w);got=primitive(minors(u,w));if(got!=q){P6 neg=q;for(I&x:neg)x=-x;if(got!=neg)throw std::runtime_error("saturated wedge");for(I&x:w)x=-x;}return {u,w};}
I dot(const V4&a,const V4&b){I s=0;for(int i=0;i<4;++i)s+=a[i]*b[i];return s;} I norm2(const V4&a){return dot(a,a);} 
I nearest_ratio(I num,I den){bool neg=num<0;I a=std::llabs(num);I q=a/den,r=a%den;I m=q+(2*r>den?1:0);return neg?-m:m;}
void positive_sign(V4&v){for(I x:v)if(x){if(x<0)for(I&y:v)y=-y;return;}}
void gauss_reduce(V4&u,V4&w){for(;;){I nu=norm2(u),nw=norm2(w);if(nw<nu||(nw==nu&&w<u)){std::swap(u,w);continue;}I m=nearest_ratio(dot(u,w),nu);if(m==0)break;for(int i=0;i<4;++i)w[i]-=m*u[i];}positive_sign(u);positive_sign(w);}
struct Fr{I n,d;}; Fr reduce(Fr a){I g=igcd(std::llabs(a.n),std::llabs(a.d));if(a.d<0)g=-g;return {a.n/g,a.d/g};} bool ge(Fr a,Fr b){return (__int128)a.n*b.d>=(__int128)b.n*a.d;} bool gt(Fr a,Fr b){return (__int128)a.n*b.d>(__int128)b.n*a.d;} 
I ceil_minus_one(I n,I d){return (n-1)/d;}
struct Cert{I p,r,q;std::array<Fr,4> gap;I A,B,speed;};
Cert find_cert(const V4&u,const V4&w){for(I q=1;q<=17;++q)for(I p=0;p<q;++p)for(I r=0;r<q;++r){std::array<Fr,4> g{};bool ok=true;for(int i=0;i<4;++i){I phase=mod(u[i]*p+w[i]*r,q);I dist=std::min(phase,q-phase);Fr gap=reduce({4*dist-q,4*q});if(!ge(gap,{1,28})){ok=false;break;}g[i]=gap;}if(!ok)continue;Fr alpha{0,1},beta{0,1};for(int i=0;i<4;++i){Fr a=reduce({std::llabs(w[i])*g[i].d,2*g[i].n});Fr b=reduce({std::llabs(u[i])*g[i].d,2*g[i].n});if(gt(a,alpha))alpha=a;if(gt(b,beta))beta=b;}I A=ceil_minus_one(alpha.n,alpha.d),B=ceil_minus_one(beta.n,beta.d);I speed=0;for(int i=0;i<4;++i)speed=std::max<I>(speed, I(A*std::llabs(u[i])+B*std::llabs(w[i])));if(speed<=290)return {p,r,q,g,A,B,speed};}
    throw std::runtime_error("no q<=17 certificate with bound<=290");}
std::vector<P6> read_pluecker(const std::string&path){std::ifstream f(path);if(!f)throw std::runtime_error("open input");std::string line;std::getline(f,line);std::vector<P6> out;while(std::getline(f,line)){if(line.empty())continue;std::stringstream ss(line);P6 p{};for(int i=0;i<6;++i){std::string x;if(!std::getline(ss,x,','))throw std::runtime_error("csv");p[i]=std::stoll(x);}out.push_back(p);}return out;}
int main(int argc,char**argv){try{if(argc!=4){std::cerr<<"usage: generate_plane_data canonical_pluecker.csv plane_classes.csv plane_safe_points.csv\n";return 2;}auto reps=read_pluecker(argv[1]);if(reps.size()!=6866)throw std::runtime_error("expected 6866 canonical classes");std::ofstream fc(argv[2]),fs(argv[3]);fc<<"p12,p13,p14,p23,p24,p34,u1,u2,u3,u4,w1,w2,w3,w4\n";fs<<"p12,p13,p14,p23,p24,p34,x_num,y_num,den,delta1_num,delta1_den,delta2_num,delta2_den,delta3_num,delta3_den,delta4_num,delta4_den,A_bound,B_bound\n";I maxspeed=0,maxq=0;Fr mingap{1,1};int n=0;for(P6 p:reps){auto [u,w]=basis_from_relation_pluecker(p);gauss_reduce(u,w);auto c=find_cert(u,w);maxspeed=std::max(maxspeed,c.speed);maxq=std::max(maxq,c.q);for(auto g:c.gap)if(gt(mingap,g))mingap=g;for(int i=0;i<6;++i){if(i)fc<<',';fc<<p[i];}for(I x:u)fc<<','<<x;for(I x:w)fc<<','<<x;fc<<'\n';for(int i=0;i<6;++i){if(i)fs<<',';fs<<p[i];}fs<<','<<c.p<<','<<c.r<<','<<c.q;for(auto g:c.gap)fs<<','<<g.n<<','<<g.d;fs<<','<<c.A<<','<<c.B<<'\n';++n;if(n%500==0)std::cerr<<"generated "<<n<<"/6866\n";}std::cout<<"generated plane classes = "<<n<<"\nmaximum certified speed bound = "<<maxspeed<<"\nminimum safety margin = "<<mingap.n<<'/'<<mingap.d<<"\nmaximum denominator = "<<maxq<<"\n";return 0;}catch(const std::exception&e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 1;}}
