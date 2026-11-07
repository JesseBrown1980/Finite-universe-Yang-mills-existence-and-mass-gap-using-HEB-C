// Independent GMP-only outward-rounded symmetric Schur inertia of projected
// integer S3 gauge Hamiltonians. No floating point or JSON.
#include <gmpxx.h>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>
#include <stdexcept>
#include <string>
using I=mpz_class;
struct Iv {I lo,hi;};
using Mat=std::vector<std::map<int,Iv>>;
static Iv quotient(const Iv& a,const Iv& b,const Iv& d){
 if(d.lo<=0&&d.hi>=0)throw std::runtime_error("UNCERTAIN_PIVOT");
 I p[4]={a.lo*b.lo,a.lo*b.hi,a.hi*b.lo,a.hi*b.hi};
 I lo=*std::min_element(p,p+4),hi=*std::max_element(p,p+4);
 I dl=d.lo,dh=d.hi;
 if(dh<0){const I q=lo;lo=-hi;hi=-q;const I x=dl;dl=-dh;dh=-x;}
 Iv z;
 if(lo>=0){mpz_fdiv_q(z.lo.get_mpz_t(),lo.get_mpz_t(),dh.get_mpz_t());mpz_cdiv_q(z.hi.get_mpz_t(),hi.get_mpz_t(),dl.get_mpz_t());}
 else if(hi<=0){mpz_fdiv_q(z.lo.get_mpz_t(),lo.get_mpz_t(),dl.get_mpz_t());mpz_cdiv_q(z.hi.get_mpz_t(),hi.get_mpz_t(),dh.get_mpz_t());}
 else {mpz_fdiv_q(z.lo.get_mpz_t(),lo.get_mpz_t(),dl.get_mpz_t());mpz_cdiv_q(z.hi.get_mpz_t(),hi.get_mpz_t(),dl.get_mpz_t());}
 return z;
}
static void put(Mat& a,int i,int j,const Iv& v){
 if(v.lo==0&&v.hi==0){a[i].erase(j);if(i!=j)a[j].erase(i);}
 else {a[i][j]=v;if(i!=j)a[j][i]=v;}
}
static Mat load(const char* path,long threshold){
 std::ifstream in(path);int n;
 if(!(in>>n)||n<1||n>6000)throw std::runtime_error("BAD_DIM");
 std::vector<int>w(n),mag(n);
 for(auto& v:w)if(!(in>>v)||v<=0)throw std::runtime_error("BAD_WEIGHT");
 for(auto& v:mag)if(!(in>>v))throw std::runtime_error("BAD_MAG");
 I scale=1;for(int i=0;i<90;++i)scale*=10;
 Mat a(n);int i,j,z,count=0;
 while(in>>i>>j>>z){
  if(i<0||i>j||j>=n||a[i].count(j))throw std::runtime_error("BAD_MATRIX");
  I value=I(w[i])*I(z)*I(1000000)*scale;
  put(a,i,j,{value,value});++count;
 }
 if(count<n)throw std::runtime_error("INCOMPLETE");
 for(int k=0;k<n;++k){
  I x=I(w[k])*I(threshold)*scale;
  auto it=a[k].find(k);Iv v=(it==a[k].end())?Iv{0,0}:it->second;
  put(a,k,k,{v.lo-x,v.hi-x});
 }
 return a;
}
static int solve(Mat& a){
 const int n=static_cast<int>(a.size());
 std::vector<char> active(n,1);int neg=0;
 for(int round=0;round<n;++round){
  int p=-1;size_t degree=static_cast<size_t>(-1);
  for(int i=0;i<n;++i)if(active[i]){
   auto it=a[i].find(i);if(it==a[i].end())continue;
   const Iv& v=it->second;
   if((v.lo>0||v.hi<0)&&a[i].size()<degree){p=i;degree=a[i].size();}
  }
  if(p<0)throw std::runtime_error("UNCERTAIN_PIVOTS_AT_"+std::to_string(round));
  Iv d=a[p].at(p);neg+=(d.hi<0);
  std::vector<std::pair<int,Iv>> nb;
  for(const auto& e:a[p])if(e.first!=p)nb.push_back(e);
  for(size_t x=0;x<nb.size();++x){
   const int i=nb[x].first;
   for(size_t y=x;y<nb.size();++y){
    const int j=nb[y].first;
    const Iv q=quotient(nb[x].second,nb[y].second,d);
    auto it=a[i].find(j);Iv old=(it==a[i].end())?Iv{0,0}:it->second;
    put(a,i,j,{old.lo-q.hi,old.hi-q.lo});
   }
  }
  for(const auto& e:nb)a[e.first].erase(p);
  a[p].clear();active[p]=0;
 }
 return neg;
}
int main(int argc,char** argv){try{
 if(argc!=3)throw std::runtime_error("USAGE FILE THRESHOLD_DIV_1000000");
 long t=std::stol(argv[2]);Mat matrix=load(argv[1],t);
 const int n=static_cast<int>(matrix.size());const int count=solve(matrix);
 std::cout<<"SELECTION_GMP|dim="<<n<<"|threshold="<<t<<"/1000000"
          <<"|negative="<<count<<"|pivots="<<n<<"/"<<n
          <<"|interval=GMP_OUTWARD|zero_pivots=0|json=0\n";
 return 0;
 }catch(const std::exception& e){
 std::cerr<<"SELECTION_GMP|FAIL="<<e.what()<<"|json=0\n";return 2;
 }
}
