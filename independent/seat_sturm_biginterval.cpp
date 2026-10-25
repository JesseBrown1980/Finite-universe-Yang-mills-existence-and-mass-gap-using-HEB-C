// Independent direct Sturm inertia certificate, no rank-one modification.
// All Schur entries are GMP integer intervals scaled by 10^100. Every
// division rounds outward. A pivot interval crossing zero fails closed.
// Matrix comes from separately built permutation-group finite S3 operator.
// NO JSON, NO FLOATS. Integer arithmetic only.
#include <gmpxx.h>
#include <algorithm>
#include <climits>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using Int=mpz_class;
struct Iv{Int lo,hi;};
using Matrix=std::vector<std::map<int,Iv>>;
static Iv quotient(Iv a,Iv b,Iv d){
    if(d.lo<=0&&d.hi>=0)throw std::runtime_error("uncertain pivot");
    Int products[4]={a.lo*b.lo,a.lo*b.hi,a.hi*b.lo,a.hi*b.hi};
    Int mn=products[0],mx=products[0];
    for(int k=1;k<4;++k){
        if(products[k]<mn)mn=products[k];
        if(products[k]>mx)mx=products[k];
    }
    if(d.hi<0){
        const Int old=mn;mn=-mx;mx=-old;
        const Int dlo=d.lo;d.lo=-d.hi;d.hi=-dlo;
    }
    if(d.lo<=0)throw std::runtime_error("nonpositive denominator");
    Iv q;
    if(mn>=0){
        mpz_fdiv_q(q.lo.get_mpz_t(),mn.get_mpz_t(),d.hi.get_mpz_t());
        mpz_cdiv_q(q.hi.get_mpz_t(),mx.get_mpz_t(),d.lo.get_mpz_t());
    }else if(mx<=0){
        mpz_fdiv_q(q.lo.get_mpz_t(),mn.get_mpz_t(),d.lo.get_mpz_t());
        mpz_cdiv_q(q.hi.get_mpz_t(),mx.get_mpz_t(),d.hi.get_mpz_t());
    }else{
        mpz_fdiv_q(q.lo.get_mpz_t(),mn.get_mpz_t(),d.lo.get_mpz_t());
        mpz_cdiv_q(q.hi.get_mpz_t(),mx.get_mpz_t(),d.lo.get_mpz_t());
    }
    return q;
}
static void put(Matrix& a,int i,int j,const Iv& x){
    if(x.lo==0&&x.hi==0){a[i].erase(j);if(i!=j)a[j].erase(i);}
    else {a[i][j]=x;if(i!=j)a[j][i]=x;}
}
static void erase_pivot(Matrix& a,int k){
    for(const auto& [j,v]:a[k])if(j!=k)a[j].erase(k);
    a[k].clear();
}
static void step(Matrix& a,int k,int& neg){
    const Iv d=a[k].at(k);
    if(d.lo<=0&&d.hi>=0)throw std::runtime_error("ambiguous elimination pivot");
    neg+=(d.hi<0);
    std::vector<std::pair<int,Iv>> nb;
    for(const auto& e:a[k])if(e.first!=k)nb.push_back(e);
    for(size_t x=0;x<nb.size();++x){
        const int i=nb[x].first;
        for(size_t y=x;y<nb.size();++y){
            const int j=nb[y].first;
            const Iv change=quotient(nb[x].second,nb[y].second,d);
            const auto it=a[i].find(j);
            const Iv old=it==a[i].end()?Iv{0,0}:it->second;
            put(a,i,j,{old.lo-change.hi,old.hi-change.lo});
        }
    }
    erase_pivot(a,k);
}
static Matrix read_matrix(const char* path,int je,int jb,int tn){
    std::ifstream in(path);
    int n=0;if(!(in>>n)||n!=1393)throw std::runtime_error("dimension");
    std::vector<int> w(n),mag(n);
    for(auto& v:w)if(!(in>>v)||v<=0)throw std::runtime_error("weight");
    for(auto& v:mag)if(!(in>>v))throw std::runtime_error("magnetic");
    Int scale=1;
    for(int i=0;i<100;++i)scale*=10;
    Matrix a(n);int i,j,z,entries=0;
    while(in>>i>>j>>z){
        if(i<0||j<i||j>=n||a[i].count(j))
            throw std::runtime_error("invalid sparse matrix");
        if(z){
            Int val=Int(1000L*je*w[i]*z)*scale;
            put(a,i,j,{val,val});++entries;
        }
    }
    if(entries<15000)throw std::runtime_error("matrix incomplete");
    for(int k=0;k<n;++k){
        const Int d=Int(1000L*jb*mag[k]*w[k]-1L*tn*w[k])*scale;
        const auto it=a[k].find(k);
        const Iv v=it==a[k].end()?Iv{0,0}:it->second;
        put(a,k,k,{v.lo+d,v.hi+d});
    }
    return a;
}
static bool directed_unit_tests(){
    for(int al=-3;al<=3;++al)for(int ah=al;ah<=3;++ah)
    for(int bl=-3;bl<=3;++bl)for(int bh=bl;bh<=3;++bh)
    for(int dl=1;dl<=3;++dl)for(int dh=dl;dh<=3;++dh)
    for(int s:{-1,1}){
        const Iv d=s==1?Iv{dl,dh}:Iv{-dh,-dl};
        const Iv q=quotient({al,ah},{bl,bh},d);
        for(int x=al;x<=ah;++x)for(int y=bl;y<=bh;++y)
        for(int z=dl;z<=dh;++z){
            const Int n=x*y,den=s*z;
            Int lo,hi;
            mpz_fdiv_q(lo.get_mpz_t(),n.get_mpz_t(),den.get_mpz_t());
            mpz_cdiv_q(hi.get_mpz_t(),n.get_mpz_t(),den.get_mpz_t());
            if(q.lo>lo||q.hi<hi)return false;
        }
    }
    return true;
}
int main(int argc,char** argv){
    try{
        if(!directed_unit_tests())throw std::runtime_error("arithmetic unit test failure");
        if(argc==2&&std::string(argv[1])=="--selftest"){
            std::cout<<"HEBC-STURM-BIG|result=PASS|selftest=PASS|json=0\n";
            return 0;
        }
        if(argc!=5)throw std::runtime_error("usage: verifier MATRIX JE JB THRESHOLD_NUM");
        const int je=std::stoi(argv[2]),jb=std::stoi(argv[3]),t=std::stoi(argv[4]);
        Matrix a=read_matrix(argv[1],je,jb,t);
        const int n=int(a.size());
        std::vector<bool> active(n,true);
        int neg=0;
        for(int pass=0;pass<n;++pass){
            int selected=-1,degree=INT_MAX;
            for(int i=0;i<n;++i)if(active[i]){
                const auto it=a[i].find(i);
                if(it==a[i].end()||(it->second.lo<=0&&it->second.hi>=0))continue;
                const int d=int(a[i].size());
                if(d<degree){degree=d;selected=i;}
            }
            if(selected<0){
                std::cout<<"HEBC-STURM-BIG|result=UNCERTAIN|pivots="<<pass<<"/"<<n
                         <<"|negative_prefix="<<neg<<"|json=0\n";
                return 2;
            }
            step(a,selected,neg);active[selected]=false;
            if(pass%100==99||pass+1==n)
                std::cout<<"HEBC-STURM-BIG-PROGRESS|pivots="<<pass+1
                         <<"/"<<n<<"|negative="<<neg<<"|json=0\n"<<std::flush;
        }
        std::cout<<"HEBC-STURM-BIG|result="<<(neg==1?"PASS":"FAIL")
                 <<"|method=GMP_INTEGER_OUTWARD_INTERVAL_LDL"
                 <<"|precision_digits=100|JE="<<je<<"|JB="<<jb
                 <<"|threshold="<<t<<"/1000|pivots="<<n
                 <<"|negative="<<neg<<"|zero=0|full_E1_inertia_certified="
                 <<(neg==1?1:0)<<"|json=0\n";
        return neg==1?0:2;
    }catch(const std::exception&e){
        std::cerr<<"HEBC-STURM-BIG|result=FAIL|reason="<<e.what()<<"|json=0\n";
        return 2;
    }
}
