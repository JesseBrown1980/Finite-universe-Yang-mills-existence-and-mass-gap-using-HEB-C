// Independent S3 symmetry-orbit electric row reconstruction, exact integers.
// Modes: --small LX LY, --pilot PASSA VECTOR FIRST COUNT.
// 3x4 pilot consumes externally hashed inputs verified by gpt6_http0_stream_inputs.py.
// C++17, read-only, integer only, no external dependencies.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;

using Links = array<uint8_t, 24>;
struct Group {
    array<array<uint8_t,3>,6> perm{};
    array<array<uint8_t,6>,6> mul{}, conjugate{};
    array<uint8_t,6> inv{};
    array<uint8_t,3> tau{};
    Group() {
        array<int,3> a = {0,1,2};
        for(int i=0;i<6;++i){
            perm[i]={uint8_t(a[0]),uint8_t(a[1]),uint8_t(a[2])};
            next_permutation(a.begin(),a.end());
        }
        auto find = [&](const array<uint8_t,3>& q)->uint8_t {
            for(int i=0;i<6;++i) if(q==perm[i]) return uint8_t(i);
            throw runtime_error("invalid S3 product");
        };
        for(int i=0;i<6;++i)for(int j=0;j<6;++j){
            array<uint8_t,3> c{};
            for(int k=0;k<3;++k)c[k]=perm[i][perm[j][k]];
            mul[i][j]=find(c);
        }
        int nt=0;
        for(int i=0;i<6;++i){
            for(int j=0;j<6;++j)if(mul[i][j]==0)inv[i]=uint8_t(j);
            if(i>0 && mul[i][i]==0)tau[nt++]=uint8_t(i);
        }
        if(nt!=3) throw runtime_error("transposition census");
        for(int c=0;c<6;++c)for(int a0=0;a0<6;++a0)
            conjugate[c][a0]=mul[mul[c][a0]][inv[c]];
    }
};
struct Op { array<uint8_t,24> dest{}; array<uint8_t,24> inverse{}; };
struct Geometry {
    Group g;
    int lx,ly,v,nl,nf;
    array<array<int,2>,24> ends{};
    vector<array<int,3>> spanning;
    vector<int> freeLinks;
    vector<array<int,4>> squares;
    vector<Op> ops;
    explicit Geometry(int x,int y):lx(x),ly(y),v(x*y),nl(2*v),nf(v+1) {
        if(lx<2||ly<2||v>12)throw runtime_error("lattice range");
        array<uint8_t,24> inTree{};
        for(int x0=0;x0<lx;++x0)for(int y0=0;y0<ly;++y0){
            ends[xedge(x0,y0)]={site(x0,y0),site(x0+1,y0)};
            ends[yedge(x0,y0)]={site(x0,y0),site(x0,y0+1)};
            squares.push_back({xedge(x0,y0),yedge(x0+1,y0),xedge(x0,y0+1),yedge(x0,y0)});
        }
        for(int y0=0;y0<ly-1;++y0){int e=yedge(0,y0);inTree[e]=1;spanning.push_back({site(0,y0),site(0,y0+1),e});}
        for(int x0=0;x0<lx-1;++x0)for(int y0=0;y0<ly;++y0){int e=xedge(x0,y0);inTree[e]=1;spanning.push_back({site(x0,y0),site(x0+1,y0),e});}
        for(int e=0;e<nl;++e)if(!inTree[e])freeLinks.push_back(e);
        if(int(freeLinks.size())!=nf)throw runtime_error("free-link rank");
        for(int fx=0;fx<2;++fx)for(int fy=0;fy<2;++fy)
            for(int tx=0;tx<lx;++tx)for(int ty=0;ty<ly;++ty){
                Op op;
                for(int x0=0;x0<lx;++x0)for(int y0=0;y0<ly;++y0){
                    int px=fx?-x0:x0, py=fy?-y0:y0;
                    int a=xedge(x0,y0), b=yedge(x0,y0);
                    op.dest[a]=uint8_t(xedge((fx?px-1:px)+tx,py+ty));
                    op.dest[b]=uint8_t(yedge(px+tx,(fy?py-1:py)+ty));
                    op.inverse[a]=uint8_t(fx);
                    op.inverse[b]=uint8_t(fy);
                }
                ops.push_back(op);
            }
        if(int(ops.size())!=4*v)throw runtime_error("symmetry size");
    }
    int site(int x,int y)const{return (x%lx+lx)%lx*ly+(y%ly+ly)%ly;}
    int xedge(int x,int y)const{return site(x,y);}
    int yedge(int x,int y)const{return v+site(x,y);}
    void unpack(uint64_t code,Links& links)const{
        links.fill(0);
        for(int e:freeLinks){links[e]=uint8_t(code%6);code/=6;}
        if(code)throw runtime_error("raw orbit key outside rank");
    }
    uint64_t encode(const array<uint8_t,13>& q,int c)const{
        uint64_t n=0;
        for(int k=nf-1;k>=0;--k)n=n*6+g.conjugate[c][q[k]];
        return n;
    }
    void orbit(const Links& U, uint64_t* best, set<uint64_t>* images)const{
        Links T{};
        array<uint8_t,12> gauge{};
        array<uint8_t,13> q{};
        uint64_t lo=numeric_limits<uint64_t>::max();
        for(const Op& op:ops){
            for(int e=0;e<nl;++e) T[op.dest[e]]=op.inverse[e]?g.inv[U[e]]:U[e];
            gauge.fill(0);
            for(const auto& s:spanning)gauge[s[1]]=g.mul[gauge[s[0]]][T[s[2]]];
            for(int k=0;k<nf;++k){
                int e=freeLinks[k];
                q[k]=g.mul[g.mul[gauge[ends[e][0]]][T[e]]][g.inv[gauge[ends[e][1]]]];
            }
            for(int c=0;c<6;++c){
                auto x=encode(q,c);
                if(x<lo)lo=x;
                if(images)images->insert(x);
            }
        }
        *best=lo;
    }
    uint64_t canon(const Links& U)const{uint64_t k;orbit(U,&k,nullptr);return k;}
    int mag(const Links& u)const{
        int cost=0;
        for(auto p:squares){
            int hol=g.mul[g.mul[g.mul[u[p[0]]][u[p[1]]]][g.inv[u[p[2]]]]][g.inv[u[p[3]]]];
            int fixed=0;
            for(int a=0;a<3;++a)fixed+=(g.perm[hol][a]==a);
            cost+=3-fixed;
        }
        return cost;
    }
    struct Edge { uint64_t key; int multiple; };
    vector<Edge> moves(uint64_t key)const{
        Links U{};unpack(key,U);
        vector<uint64_t> all;all.reserve(size_t(nl)*3);
        for(int e=0;e<nl;++e){
            int saved=U[e];
            for(uint8_t t:g.tau){ U[e]=g.mul[t][saved]; all.push_back(canon(U)); }
            U[e]=uint8_t(saved);
        }
        sort(all.begin(),all.end());
        vector<Edge> ret;
        for(size_t i=0;i<all.size();){size_t j=i+1;while(j<all.size()&&all[j]==all[i])++j;
            ret.push_back({all[i],int(j-i)});i=j;}
        return ret;
    }
};

static void require(bool good,const string& what){if(!good)throw runtime_error(what);}

static int small(int lx,int ly){
    Geometry m(lx,ly);
    uint64_t raw=1;for(int i=0;i<m.nf;++i)raw*=6;
    vector<uint64_t> ids;
    Links u{};
    for(uint64_t k=0;k<raw;++k){m.unpack(k,u);if(m.canon(u)==k)ids.push_back(k);}
    uint64_t expect=(raw+3*(uint64_t(1)<<m.nf)+2*([&](){uint64_t z=1;for(int k=0;k<m.nf;++k)z*=3;return z;}()))/6;
    // Periodic reflection/translational symmetry reduces the physical-orbit count.
    const uint64_t ref=(lx==2 && ly==2)?211:(lx==2 && ly==3)?2646:0;
    require(ref!=0 && ids.size()==ref,"symmetry-sector orbit census");
    uint64_t weightSum=0,flat=0,flatW=0,pairs=0,bad=0;
    vector<int> weights(ids.size());
    for(size_t i=0;i<ids.size();++i){
        m.unpack(ids[i],u);
        set<uint64_t> orbitCodes;
        uint64_t k;m.orbit(u,&k,&orbitCodes);
        require(k==ids[i],"noncanonical orbit key");
        weights[i]=int(orbitCodes.size());
        weightSum+=weights[i];
        if(m.mag(u)==0){flat++;flatW+=weights[i];}
    }
    vector<vector<Geometry::Edge>> allRows;
    allRows.reserve(ids.size());
    for(auto key:ids)allRows.push_back(m.moves(key));
    for(size_t i=0;i<ids.size();++i){
        int n=0;
        for(auto a:allRows[i]){
            n+=a.multiple;
            auto it=lower_bound(ids.begin(),ids.end(),a.key);
            require(it!=ids.end() && *it==a.key,"electric transition census");
            size_t j=size_t(it-ids.begin());
            auto &rev=allRows[j];
            auto rit=lower_bound(rev.begin(),rev.end(),ids[i],[](auto b,uint64_t key){return b.key<key;});
            if(rit==rev.end()||rit->key!=ids[i]||uint64_t(weights[i])*uint64_t(a.multiple)!=uint64_t(weights[j])*uint64_t(rit->multiple))bad++;
            pairs++;
        }
        require(n==3*m.nl,"move conservation");
    }
    require(weightSum==raw&&bad==0&&flat==7&&flatW==18,"small sector invariants");
    cout<<"HTTP0_YM_SECTOR_REBUILD|lattice="<<lx<<'x'<<ly<<"|physical_orbits="<<expect
        <<"|sector_rows="<<ids.size()<<"|orbit_weight_sum="<<weightSum<<"|flat_rows="<<flat
        <<"|flat_weight_sum="<<flatW<<"|checked_edges="<<pairs<<"|weighted_mismatches="<<bad
        <<"|status=PASS|json=0\n";
    return 0;
}

static uint32_t u32(const uint8_t *p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
static uint64_t u64(const uint8_t *p){uint64_t n=0;for(int b=7;b>=0;--b)n=n*256+p[b];return n;}
static int64_t i64(const uint8_t *p){return static_cast<int64_t>(u64(p));}

static int pilot(const string& keyfile,const string& vecfile,size_t first,size_t count,const string& sabotage,bool leaf,bool shard=false){
    constexpr size_t N=45508080;
    require(first<N && count>0 && count<=(shard?29U*59049U:(leaf?59049U:128U)) && first+count<=N,"sample bounds");
    vector<uint8_t> kb(N*16),db(N*8);
    ifstream f(keyfile,ios::binary),g(vecfile,ios::binary);
    require(f.good() && g.good(),"original inputs");
    require(bool(f.read(reinterpret_cast<char*>(kb.data()),streamsize(kb.size()))),"key table read");
    require(bool(g.read(reinterpret_cast<char*>(db.data()),streamsize(db.size()))),"vector read");
    if(sabotage=="tamper-weight")kb[first*16+8]=0;
    if(sabotage=="tamper-vector")for(int j=0;j<8;++j)db[first*8+j]=0;
    auto getkey=[&](size_t h)->uint64_t{return u64(&kb[h*16]);};
    auto getw=[&](size_t h)->uint32_t{return u32(&kb[h*16+8]);};
    auto getmag=[&](size_t h)->uint32_t{return u32(&kb[h*16+12]);};
    auto getd=[&](size_t h)->int64_t{return i64(&db[h*8]);};
    Geometry m(3,4);
    uint64_t checked=0,adjChecked=0;
    int64_t minRatio=numeric_limits<int64_t>::max();
    size_t minRow=first;
    uint64_t weightSum=0,flats=0,electricMoves=0;
    size_t leafStart=first;
    uint64_t totalCount=0,completedLeaves=0;
    for(size_t h=first;h<first+count;++h){
        Links u{};m.unpack(getkey(h),u);
        require(m.canon(u)==getkey(h),"sector key");
        require(uint32_t(m.mag(u))==getmag(h),"magnetic cost");
        set<uint64_t> images;uint64_t k;m.orbit(u,&k,&images);
        require(images.size()==getw(h),"orbit weight");
        weightSum+=getw(h);
        auto row=m.moves(getkey(h));
        __int128 accumulator=(__int128(72)+__int128(9)*getmag(h))*getd(h);
        int countMoves=0;
        for(const auto& a:row){
            size_t lo=0,hi=N;
            while(lo<hi){size_t mid=lo+(hi-lo)/2;if(getkey(mid)<a.key)lo=mid+1;else hi=mid;}
            require(lo<N && getkey(lo)==a.key,"electric target in key table");
            countMoves+=a.multiple;
            accumulator-=__int128(a.multiple)*getd(lo);
            if(adjChecked<8 && lo!=h){
                auto reverse=m.moves(a.key);
                auto rit=lower_bound(reverse.begin(),reverse.end(),getkey(h),[](auto e,uint64_t key){return e.key<key;});
                require(rit!=reverse.end() && rit->key==getkey(h),"reverse electric move");
                require(uint64_t(getw(h))*uint64_t(a.multiple)==uint64_t(getw(lo))*uint64_t(rit->multiple),"weighted adjoint");
                ++adjChecked;
            }
        }
        require(countMoves==72,"move count");
        electricMoves+=uint64_t(countMoves);
        if(leaf && (checked+1)%8192==0) cerr<<"HTTP0_YM_LEAF_PROGRESS|first="<<first<<"|done="<<checked+1<<"|of="<<count<<"|json=0\n";
        if(getmag(h)==0){require(getd(h)==0,"flat vector");++flats;}
        else{
            require(getd(h)>0,"strict comparison vector");
            int64_t ratio=int64_t((accumulator*1000000)/getd(h));
            if(ratio<minRatio){minRatio=ratio;minRow=h;}
            require(ratio>=94070673,"Perron bound refutation");
            if(h==45507968ULL)require(ratio==94070673,"tight Perron row");
        }
        ++checked;
        ++totalCount;
        if(shard && (((h+1)%59049U)==0 || (h+1)==first+count)){
            cout<<"HTTP0_YM_REBUILT_LEAF|first="<<leafStart<<"|rows="<<checked
                <<"|electric_moves="<<electricMoves<<"|orbit_weight_sum="<<weightSum
                <<"|flats="<<flats<<"|min_row="<<minRow<<"|min_ratio_microJE="<<minRatio
                <<"|reverse_pairs="<<adjChecked<<"|bound_microJE=94070673|status=PASS|json=0\n";
            cout.flush();
            leafStart=h+1;
            checked=0;
            ++completedLeaves;
            adjChecked=weightSum=flats=electricMoves=0;
            minRow=leafStart;
            minRatio=numeric_limits<int64_t>::max();
        }
    }
    if(shard){
        cout<<"HTTP0_YM_SHARD|id="<<(first/(29U*59049U))<<"|first="<<first
            <<"|rows="<<totalCount<<"|leaves="<<completedLeaves
            <<"|status=PASS|json=0\n";
    }else if(leaf){
        cout<<"HTTP0_YM_REBUILT_LEAF|first="<<first<<"|rows="<<checked
            <<"|electric_moves="<<electricMoves<<"|orbit_weight_sum="<<weightSum
            <<"|flats="<<flats<<"|min_row="<<minRow<<"|min_ratio_microJE="<<minRatio
            <<"|reverse_pairs="<<adjChecked<<"|bound_microJE=94070673|status=PASS|json=0\n";
    }else{
        cout<<"HTTP0_YM_ROW_PILOT|first="<<first<<"|rows="<<checked<<"|verified_reverse_pairs="<<adjChecked
            <<"|min_sample_ratio_microJE="<<(minRatio==numeric_limits<int64_t>::max()?0:minRatio)
            <<"|bound_microJE=94070673|status=PASS|json=0\n";
    }
    return 0;
}
int main(int argc,char** argv){try{
    if(argc==4 && string(argv[1])=="--small")return small(stoi(argv[2]),stoi(argv[3]));
    if(argc==5 && string(argv[1])=="--shard"){
        constexpr size_t n=45508080;
        size_t id=stoull(argv[4]);
        require(id<27,"shard id");
        size_t first=id*29U*59049U;
        size_t count=min(size_t(29U*59049U),n-first);
        return pilot(argv[2],argv[3],first,count,"",true,true);
    }
    if((argc==6||argc==7) && (string(argv[1])=="--pilot" || string(argv[1])=="--leaf")){
        bool leaf=string(argv[1])=="--leaf";
        string sabotage=argc==7?string(argv[6]):string();
        require(sabotage.empty()||sabotage=="tamper-weight"||sabotage=="tamper-vector","sabotage argument");
        return pilot(argv[2],argv[3],stoull(argv[4]),stoull(argv[5]),sabotage,leaf);
    }
    cerr<<"usage: --small LX LY | --pilot PASSA VECTOR FIRST COUNT | --leaf PASSA VECTOR FIRST COUNT | --shard PASSA VECTOR ID\n";return 2;
}catch(const exception& e){cerr<<"HTTP0_YM_ROW_FAIL|reason="<<e.what()<<"|json=0\n";return 2;}}
