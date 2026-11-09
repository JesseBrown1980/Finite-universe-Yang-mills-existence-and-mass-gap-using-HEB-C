// Independent finite S3 orbit/transition verifier; no original operator builder imported.
// POST-EXPLORATION reconstruction, not a 45,508,080-row store replay.
// g++ -O3 -std=c++17 -Wall -Wextra -Werror -pedantic source.cpp -o replay
// replay 2 2 ; replay 2 3 ; replay 3 4 ; replay 3 4 sabotage
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;
struct Model {
 int lx, ly, v, nlinks, k;
 array<array<uint8_t,6>,6> mult{}, conjugates{};
 array<uint8_t,6> inverse{};
 array<array<uint8_t,3>,6> perms{};
 vector<int> freelinks;
 vector<array<int,3>> tree;
 vector<array<int,2>> endpoints;
 vector<array<int,4>> plaq;
 vector<uint8_t> trans;
 int vertex(int x,int y) const { x=(x%lx+lx)%lx; y=(y%ly+ly)%ly; return x*ly+y; }
 int ax(int x,int y) const { return vertex(x,y); }
 int ay(int x,int y) const { return v+vertex(x,y); }
 Model(int x,int y):lx(x),ly(y),v(x*y),nlinks(2*x*y) {
  if(x<2||y<2||x*y>12) throw 1;
  int n=0; array<int,3> a={0,1,2};
  do {perms[n++]={uint8_t(a[0]),uint8_t(a[1]),uint8_t(a[2])};} while(next_permutation(a.begin(),a.end()));
  auto lookup=[&](array<uint8_t,3> p){for(int i=0;i<6;++i)if(perms[i]==p)return i;std::abort();};
  for(int i=0;i<6;++i)for(int j=0;j<6;++j){
   array<uint8_t,3> p{};
   for(int t=0;t<3;++t)p[t]=perms[i][perms[j][t]];
   mult[i][j]=lookup(p);
  }
  for(int i=0;i<6;++i)for(int j=0;j<6;++j)if(mult[i][j]==0)inverse[i]=j;
  for(int c=0;c<6;++c)for(int b=0;b<6;++b)conjugates[c][b]=mult[mult[c][b]][inverse[c]];
  for(int i=1;i<6;++i)if(mult[i][i]==0)trans.push_back(i);
  if(trans.size()!=3)throw 2;
  endpoints.resize(nlinks);
  for(int i=0;i<lx;++i)for(int j=0;j<ly;++j){
   endpoints[ax(i,j)]={vertex(i,j),vertex(i+1,j)};
   endpoints[ay(i,j)]={vertex(i,j),vertex(i,j+1)};
   plaq.push_back({ax(i,j),ay(i+1,j),ax(i,j+1),ay(i,j)});
  }
  vector<bool> isTree(nlinks,false);
  for(int j=0;j<ly-1;++j){int e=ay(0,j);isTree[e]=true;tree.push_back({vertex(0,j),vertex(0,j+1),e});}
  for(int i=0;i<lx-1;++i)for(int j=0;j<ly;++j){int e=ax(i,j);isTree[e]=true;tree.push_back({vertex(i,j),vertex(i+1,j),e});}
  for(int e=0;e<nlinks;++e)if(!isTree[e])freelinks.push_back(e);
  k=int(freelinks.size()); if(k!=v+1)throw 3;
 }
 uint64_t code(const array<uint8_t,13>& digits) const {
  uint64_t val=0,p=1;for(int i=0;i<k;++i){val+=digits[i]*p;p*=6;}return val;
 }
 uint64_t canon(const array<uint8_t,13>& d) const {
  uint64_t best=UINT64_MAX;
  for(int c=0;c<6;++c){
   array<uint8_t,13> z{};
   for(int i=0;i<k;++i)z[i]=conjugates[c][d[i]];
   best=min(best,code(z));
  }
  return best;
 }
 void unpack(uint64_t key,vector<uint8_t>& U) const {
  fill(U.begin(),U.end(),0);
  for(int i=0;i<k;++i){U[freelinks[i]]=uint8_t(key%6);key/=6;}
 }
 uint64_t canonicalGauge(const vector<uint8_t>& U) const {
  vector<uint8_t> g(v,0);
  for(auto e:tree)g[e[1]]=mult[g[e[0]]][U[e[2]]];
  array<uint8_t,13>d{};
  for(int i=0;i<k;++i){
   int e=freelinks[i];auto ep=endpoints[e];
   d[i]=mult[mult[g[ep[0]]][U[e]]][inverse[g[ep[1]]]];
  }
  return canon(d);
 }
 int mCost(const vector<uint8_t>& U) const {
  int total=0;
  for(auto q:plaq){
   int h=mult[mult[mult[U[q[0]]][U[q[1]]]][inverse[U[q[2]]]]][inverse[U[q[3]]]];
   int fix=0;for(int i=0;i<3;++i)fix+=perms[h][i]==i;
   total+=3-fix;
  }
  return total;
 }
 int weight(uint64_t key) const {
  array<uint8_t,13>d{};for(int i=0;i<k;++i){d[i]=uint8_t(key%6);key/=6;}
  set<uint64_t>s;
  for(int c=0;c<6;++c){
   array<uint8_t,13>z{};
   for(int i=0;i<k;++i)z[i]=conjugates[c][d[i]];
   s.insert(code(z));
  }
  return int(s.size());
 }
};
int replayShell(Model &g,bool sabotage) {
 if(g.lx!=3||g.ly!=4)return 2;
 auto t0=chrono::steady_clock::now();
 vector<uint8_t>U(g.nlinks,0);
 vector<vector<uint64_t>>layers(4);
 unordered_set<uint64_t>visited;
 for(int a=0;a<6;++a)for(int b=0;b<6;++b)if(g.mult[a][b]==g.mult[b][a]){
  fill(U.begin(),U.end(),0);
  for(int y=0;y<g.ly;++y)U[g.ax(g.lx-1,y)]=uint8_t(a);
  for(int x=0;x<g.lx;++x)U[g.ay(x,g.ly-1)]=uint8_t(b);
  if(g.mCost(U)!=0)return 3;
  auto c=g.canonicalGauge(U);
  if(visited.insert(c).second)layers[0].push_back(c);
 }
 if(layers[0].size()!=8)return 4;
 for(int l=0;l<3;++l){
  for(auto key:layers[l]){
   g.unpack(key,U);
   for(int e=0;e<g.nlinks;++e){
    int old=U[e];
    for(auto t:g.trans){
     U[e]=g.mult[t][old];
     auto q=g.canonicalGauge(U);
     if(visited.insert(q).second)layers[l+1].push_back(q);
    }
    U[e]=uint8_t(old);
   }
  }
 }
 unordered_map<uint64_t,int>index;
 size_t n=layers[0].size()+layers[1].size()+layers[2].size();
 index.reserve(n*2);
 for(int l=0;l<=2;++l)for(auto key:layers[l])index.emplace(key,int(index.size()));
 vector<vector<pair<int,int>>>adj(n);
 vector<int>weights(n);
 uint64_t loops=0,internal=0,external=0,bad=0;
 for(auto &entry:index){
  uint64_t key=entry.first;int i=entry.second;
  g.unpack(key,U);weights[i]=g.weight(key);
  vector<int>targets;targets.reserve(72);
  for(int e=0;e<g.nlinks;++e){
   int old=U[e];
   for(auto t:g.trans){
    U[e]=g.mult[t][old];
    auto it=index.find(g.canonicalGauge(U));
    if(it==index.end())++external;else targets.push_back(it->second);
   }
   U[e]=uint8_t(old);
  }
  sort(targets.begin(),targets.end());
  for(size_t z=0;z<targets.size();){
   size_t j=z+1;
   while(j<targets.size()&&targets[j]==targets[z])++j;
   if(targets[z]==i)loops+=j-z;
   else{adj[i].push_back({targets[z],int(j-z)});internal+=j-z;}
   z=j;
  }
 }
 if(sabotage)weights[0]++;
 for(size_t i=0;i<n;++i)for(auto [j,m]:adj[i]){
  auto &v=adj[j];
  auto it=lower_bound(v.begin(),v.end(),int(i),[](const auto &a,int b){return a.first<b;});
  if(it==v.end()||it->first!=int(i)||uint64_t(weights[i])*m!=uint64_t(weights[j])*it->second)++bad;
 }
 uint64_t flatWeight=0;for(auto key:layers[0])flatWeight+=g.weight(key);
 uint64_t raw=1,p3=1;for(int i=0;i<g.k;++i){raw*=6;p3*=3;}
 uint64_t states=(raw+3*(1ULL<<g.k)+2*p3)/6;
 bool ok=states==2177317873ULL&&layers[0].size()==8&&layers[1].size()==264&&layers[2].size()==7770&&layers[3].size()==147344&&flatWeight==18&&bad==0&&loops+internal+external==n*72ULL;
 auto ms=chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now()-t0).count();
 cout<<"INDEPENDENT_S3_SHELL|lattice=3x4|full_orbit_count_Burnside="<<states<<"|K0="<<layers[0].size()<<"|K1="<<layers[1].size()<<"|K2="<<layers[2].size()<<"|K3_exterior="<<layers[3].size()<<"|K2_total="<<n<<"|flat_weight_sum="<<flatWeight<<"|interior_directed_moves="<<internal<<"|exterior_directed_moves="<<external<<"|self_moves="<<loops<<"|weighted_pair_failures="<<bad<<"|elapsed_ms="<<ms<<"|status="<<(ok?"PASS":"FAIL")<<"\n";
 return ok?0:5;
}
int main(int argc,char **argv){
 if(argc!=3&&argc!=4){cerr<<"usage: replay LX LY [sabotage]\n";return 2;}
 bool sabotage=argc==4&&string(argv[3])=="sabotage";
 if(argc==4&&!sabotage)return 2;
 int lx=atoi(argv[1]),ly=atoi(argv[2]);
 Model g(lx,ly);
 if(g.k==13)return replayShell(g,sabotage);
 if(g.k>7)return 2;
 auto start=chrono::steady_clock::now();
 uint64_t raw=1;for(int z=0;z<g.k;++z)raw*=6;
 vector<uint64_t>keys;keys.reserve(raw/4);
 array<uint8_t,13>d{};
 for(uint64_t i=0;i<raw;++i){
  uint64_t z=i;
  for(int j=0;j<g.k;++j){d[j]=uint8_t(z%6);z/=6;}
  if(g.canon(d)==i)keys.push_back(i);
 }
 const size_t n=keys.size();
 uint64_t orbitSum=0,flat=0,flatWeight=0,badKey=0,badEdge=0,badBalance=0;
 vector<uint8_t>U(g.nlinks);
 vector<int>weights(n);
 for(size_t i=0;i<n;++i){
  weights[i]=g.weight(keys[i]);orbitSum+=weights[i];
  g.unpack(keys[i],U);
  if(g.canonicalGauge(U)!=keys[i])++badKey;
  if(g.mCost(U)==0){++flat;flatWeight+=weights[i];}
 }
 if(orbitSum!=raw)return 3;
 if(sabotage)weights[0]++;
 vector<vector<pair<int,int>>>rows(n);
 uint64_t offPairs=0,diag=0,directedOff=0;
 for(size_t i=0;i<n;++i){
  g.unpack(keys[i],U);
  vector<int>targets;targets.reserve(size_t(3*g.nlinks));
  for(int e=0;e<g.nlinks;++e){
   int old=U[e];
   for(auto t:g.trans){
    U[e]=g.mult[t][old];
    auto id=g.canonicalGauge(U);
    auto it=lower_bound(keys.begin(),keys.end(),id);
    if(it==keys.end()||*it!=id)++badEdge;
    else targets.push_back(int(it-keys.begin()));
   }
   U[e]=uint8_t(old);
  }
  sort(targets.begin(),targets.end());
  for(size_t j=0;j<targets.size();){
   size_t e=j+1;while(e<targets.size()&&targets[e]==targets[j])++e;
   int count=int(e-j);
   if(targets[j]==int(i))diag+=count;
   else{rows[i].push_back({targets[j],count});++offPairs;directedOff+=count;}
   j=e;
  }
 }
 for(size_t i=0;i<n;++i)for(auto [j,m]:rows[i]){
  auto &r=rows[j];
  auto it=lower_bound(r.begin(),r.end(),int(i),[](const pair<int,int>&p,int target){return p.first<target;});
  if(it==r.end()||it->first!=int(i)||uint64_t(weights[i])*m!=uint64_t(weights[j])*it->second)++badBalance;
 }
 uint64_t p3=1;for(int z=0;z<g.k;++z)p3*=3;
 uint64_t expected=(raw+3*(1ULL<<g.k)+2*p3)/6;
 bool ok=n==expected&&badKey==0&&badEdge==0&&badBalance==0&&flat==8&&flatWeight==18&&orbitSum==raw&&directedOff+diag==n*uint64_t(3*g.nlinks);
 auto ms=chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now()-start).count();
 cout<<"INDEPENDENT_S3|L="<<lx<<"x"<<ly<<"|states="<<n<<"|burnside_expected="<<expected<<"|raw_keys="<<raw<<"|orbit_weight_sum="<<orbitSum<<"|flat_orbits="<<flat<<"|flat_weight_sum="<<flatWeight<<"|directed_offdiagonal_multiplicities="<<directedOff<<"|offdiagonal_row_pairs="<<offPairs<<"|self_moves="<<diag<<"|weighted_balance_failures="<<badBalance<<"|bad_keys="<<badKey<<"|bad_targets="<<badEdge<<"|elapsed_ms="<<ms<<"|status="<<(ok?"PASS":"FAIL")<<"\n";
 return ok?0:4;
}