// Independent exact-rational Sturm inertia audit of the finite 1393-state S3 torus.
// Uses the separately reconstructed operator from independent/seat_sturm_integer_matrix.py.
// No floating-point arithmetic, no JSON, no Stage 2H rank-one or approximate Cholesky.
// Sparse symmetric exact LDL, minimum-degree congruent pivot ordering; 2x2 pivot fallback.
// Build: g++ -O3 -std=c++17 -Wall -Wextra -Werror seat_sturm_exact_gmp.cpp -lgmpxx -lgmp -o exact
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
using R=mpq_class;
using Matrix=std::vector<std::map<int,R>>;
static void put(Matrix& a,int i,int j,const R& v){
    if(v==0){a[i].erase(j);if(i!=j)a[j].erase(i);}
    else{a[i][j]=v;if(i!=j)a[j][i]=v;}
}
static void subtract(Matrix& a,int i,int j,const R& v){
    if(v==0)return;
    auto it=a[i].find(j);
    R next;
    if(it==a[i].end())next=-v;
    else next=it->second-v;
    put(a,i,j,next);
}
static void drop(Matrix& a,int k){
    for(const auto& elem:a[k])if(elem.first!=k)a[elem.first].erase(k);
    a[k].clear();
}
struct Inertia{int positive=0,negative=0,zero=0,pivots=0,blocks2=0;};
static void single(Matrix& a,int k,Inertia& counts){
    const R pivot=a[k].at(k);
    counts.negative+=(mpq_sgn(pivot.get_mpq_t())<0);
    counts.positive+=(mpq_sgn(pivot.get_mpq_t())>0);
    ++counts.pivots;
    std::vector<std::pair<int,R>> neighbors;
    for(const auto& entry:a[k])if(entry.first!=k)neighbors.push_back(entry);
    const R inverse=R(1)/pivot;
    for(size_t x=0;x<neighbors.size();++x){
        const R scale=neighbors[x].second*inverse;
        for(size_t y=x;y<neighbors.size();++y)
            subtract(a,neighbors[x].first,neighbors[y].first,scale*neighbors[y].second);
    }
    drop(a,k);
}
// When every available 1x1 diagonal is zero, a 2x2 [[0,b],[b,c]]
// has determinant -b^2<0 and hence one positive, one negative eigenvalue.
static void pair_pivot(Matrix& a,int k,int l,Inertia& counts){
    const R b=a[k].at(l), c=a[l].count(l)?a[l].at(l):R(0);
    if(b==0||a[k].count(k))throw std::runtime_error("bad exact 2x2 pivot");
    std::map<int,std::pair<R,R>> neighbors;
    for(const auto& [j,v]:a[k])if(j!=l)neighbors[j].first=v;
    for(const auto& [j,v]:a[l])if(j!=k)neighbors[j].second=v;
    std::vector<std::pair<int,std::pair<R,R>>> ns(neighbors.begin(),neighbors.end());
    for(size_t x=0;x<ns.size();++x){
        const auto [a1,b1]=ns[x].second;
        for(size_t y=x;y<ns.size();++y){
            const auto [a2,b2]=ns[y].second;
            subtract(a,ns[x].first,ns[y].first,(a1*b2+b1*a2)/b-c*a1*a2/(b*b));
        }
    }
    drop(a,k);drop(a,l);
    ++counts.positive;++counts.negative;counts.pivots+=2;++counts.blocks2;
}
static Inertia exact_inertia(Matrix a,int limit,int progress){
    const int n=int(a.size()); std::vector<bool> active(n,true); Inertia counts;
    while(counts.pivots<n&&counts.pivots<limit){
        int selected=-1,degree=INT_MAX;
        for(int i=0;i<n;++i)if(active[i]&&a[i].count(i)){
            const int d=int(a[i].size());
            if(d<degree){degree=d;selected=i;}
        }
        if(selected>=0){
            single(a,selected,counts);active[selected]=false;
        }else{
            int partner=-1;
            for(int i=0;i<n;++i)if(active[i]&&!a[i].empty()){
                selected=i;
                for(const auto& [j,v]:a[i])if(j!=i){partner=j;break;}
                if(partner>=0)break;
            }
            if(partner>=0){
                if(counts.pivots+2>limit)break;
                pair_pivot(a,selected,partner,counts);
                active[selected]=active[partner]=false;
            }else{
                for(int i=0;i<n&&counts.pivots<limit;++i)if(active[i]){
                    ++counts.zero;++counts.pivots;active[i]=false;
                }
            }
        }
        if(progress>0&&(counts.pivots%progress==0||counts.pivots==n))
            std::cout<<"HEBC-EXACT-PROGRESS|pivots="<<counts.pivots<<"/"<<n
                     <<"|negative="<<counts.negative<<"|zero="<<counts.zero
                     <<"|two_by_two="<<counts.blocks2<<"|json=0\n"<<std::flush;
    }
    return counts;
}
static Matrix load(const char* path,int je,int jb,int t){
    std::ifstream in(path);int n=0;
    if(!(in>>n)||n!=1393)throw std::runtime_error("expected 1393 states");
    std::vector<int> weights(n),potential(n);
    for(auto& w:weights)if(!(in>>w)||w<=0)throw std::runtime_error("weight");
    for(auto& b:potential)if(!(in>>b))throw std::runtime_error("potential");
    Matrix a(n);int i,j,v,edges=0;
    while(in>>i>>j>>v){
        if(i<0||j<i||j>=n||a[i].count(j))
            throw std::runtime_error("invalid upper triangular sparse entry");
        if(v){put(a,i,j,R(1000L*je*weights[i]*v));++edges;}
    }
    if(edges<15000)throw std::runtime_error("incomplete operator");
    for(int k=0;k<n;++k){
        R d=R(1000L*jb*potential[k]*weights[k]-1L*t*weights[k]);
        auto it=a[k].find(k);
        if(it!=a[k].end())d+=it->second;
        put(a,k,k,d);
    }
    return a;
}
static void selftest(){
    Matrix a(2);put(a,0,1,R(2));put(a,1,1,R(3));
    auto p=exact_inertia(a,2,0);
    if(p.negative!=1||p.positive!=1||p.zero!=0||p.blocks2!=1)
        throw std::runtime_error("2x2 pivot test");
    Matrix b(3);put(b,0,0,R(4));put(b,1,1,R(-2));
    auto q=exact_inertia(b,3,0);
    if(q.negative!=1||q.positive!=1||q.zero!=1)
        throw std::runtime_error("zero eigenvalue test");
}
int main(int argc,char** argv){
    try{
        selftest();
        if(argc==2&&std::string(argv[1])=="--selftest"){
            std::cout<<"HEBC-EXACT|result=PASS|selftest=PASS|json=0\n";return 0;
        }
        if(argc!=5&&argc!=6)
            throw std::runtime_error("usage: exact MATRIX JE JB THRESHOLD_NUM [MAX_PIVOTS]");
        int je=std::stoi(argv[2]),jb=std::stoi(argv[3]),t=std::stoi(argv[4]);
        int limit=argc==6?std::stoi(argv[5]):1393;
        if(je<0||jb<0||limit<=0||limit>1393)
            throw std::runtime_error("bad parameters");
        const auto result=exact_inertia(load(argv[1],je,jb,t),limit,100);
        const bool full=result.pivots==1393;
        const bool ok=full&&result.negative==1&&result.zero==0;
        std::cout<<"HEBC-EXACT|result="<<(full?(ok?"PASS":"FAIL"):"PARTIAL_PREFIX_ONLY")
                 <<"|method=EXACT_GMP_SPARSE_RATIONAL_LDL|JE="<<je<<"|JB="<<jb
                 <<"|threshold_num="<<t<<"|threshold_den=1000|pivots="
                 <<result.pivots<<"/1393|positive="<<result.positive
                 <<"|negative="<<result.negative<<"|zero="<<result.zero
                 <<"|2x2_blocks="<<result.blocks2
                 <<"|full_E1_inertia_certified="<<(ok?1:0)<<"|json=0\n";
        return full&&!ok?2:0;
    }catch(const std::exception&e){
        std::cerr<<"HEBC-EXACT|result=FAIL|reason="<<e.what()<<"|json=0\n";return 2;
    }
}
