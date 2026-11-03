// Independent direct finite-S3 Sturm / Sylvester prefix verifier.
// Integer-only C++17; no floating point and no JSON.
// This checks the signs of successive Schur pivots of B = W*(1000 H-t_num I),
// WITHOUT the Stage 2H rank-one term or Cholesky witness.
//
// Each Schur entry has an integer interval in units of 1e-12. Every divide
// is outward-rounded; if an interval pivot contains zero, fail instead of
// deciding a sign. This yields rigorous inertia only for completed prefixes.
// Full 1393-pivot certification is NOT claimed.
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using I = __int128_t;
struct Interval { I low, high; };

I floor_div(I numerator, I positive_denominator) {
    const I q = numerator / positive_denominator;
    const I r = numerator % positive_denominator;
    return q - (r < 0);
}
I ceil_div(I numerator, I positive_denominator) {
    const I q = numerator / positive_denominator;
    const I r = numerator % positive_denominator;
    return q + (r > 0);
}
std::string decimal(I x) {
    const bool negative = x < 0;
    if (negative) x = -x;
    std::string s;
    do {
        s += static_cast<char>('0' + static_cast<int>(x % 10));
        x /= 10;
    } while (x != 0);
    if (negative) s += '-';
    std::reverse(s.begin(), s.end());
    return s;
}

// Outward enclosure of (a*b)/d over rectangular integer intervals,
// with denominator bounded away from zero. Multi-affinity means extrema
// of the numerator occur at four endpoint products. Given fixed sign
// of denominator, quotient extrema use the indicated endpoint of d.
Interval quotient(Interval a, Interval b, Interval d) {
    const I p1 = a.low * b.low;
    const I p2 = a.low * b.high;
    const I p3 = a.high * b.low;
    const I p4 = a.high * b.high;
    I pmin = std::min(std::min(p1,p2),std::min(p3,p4));
    I pmax = std::max(std::max(p1,p2),std::max(p3,p4));
    if (d.high < 0) {
        const I old_min = pmin;
        pmin = -pmax;
        pmax = -old_min;
        const I old_low = d.low;
        d.low = -d.high;
        d.high = -old_low;
    }
    if (d.low <= 0) throw std::runtime_error("UNCERTAIN: pivot contains zero");
    if (pmin >= 0) return {floor_div(pmin,d.high), ceil_div(pmax,d.low)};
    if (pmax <= 0) return {floor_div(pmin,d.low), ceil_div(pmax,d.high)};
    return {floor_div(pmin,d.low), ceil_div(pmax,d.low)};
}

bool interval_unit_tests() {
    for (int alo=-2; alo<=2; ++alo)
    for (int ahi=alo; ahi<=2; ++ahi)
    for (int blo=-2; blo<=2; ++blo)
    for (int bhi=blo; bhi<=2; ++bhi)
    for (int dlo=1; dlo<=3; ++dlo)
    for (int dhi=dlo; dhi<=4; ++dhi)
    for (int sign : {-1, 1}) {
        Interval d = sign>0 ? Interval{dlo,dhi} : Interval{-dhi,-dlo};
        const Interval r=quotient({alo,ahi},{blo,bhi},d);
        for (int x=alo; x<=ahi; ++x)
        for (int y=blo; y<=bhi; ++y)
        for (int z=dlo; z<=dhi; ++z) {
            const int signed_d=sign*z;
            const int v=x*y*(signed_d<0?-1:1);
            const int pos_d=std::abs(signed_d);
            if (r.low > floor_div(v,pos_d) ||
                r.high < ceil_div(v,pos_d)) return false;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    if (!interval_unit_tests()) {
        std::cerr << "FAIL|reason=interval quotient unit test failed|json=0\n";
        return 1;
    }
    if (argc == 2 && std::string(argv[1]) == "--selftest") {
        std::cout << "HEBC-STURM|result=PASS|interval_quotient_tests=PASS|json=0\n";
        return 0;
    }
    if (argc != 6) {
        std::cerr << "usage: seat_sturm_prefix MATRIX JE JB THRESHOLD_NUM PREFIX_SIZE\n";
        return 1;
    }
    std::ifstream input(argv[1]);
    int n=0;
    if (!(input >> n) || n != 1393) return 1;
    const int je=std::atoi(argv[2]);
    const int jb=std::atoi(argv[3]);
    const int threshold=std::atoi(argv[4]);
    const int limit=std::atoi(argv[5]);
    if (limit < 1 || limit > n || je < 0 || jb < 0 || threshold < 0) return 1;
    std::vector<int> weights(n), magnetic(n);
    for (int& x : weights) if (!(input >> x)) return 1;
    for (int& x : magnetic) if (!(input >> x)) return 1;
    std::vector<Interval> upper(static_cast<size_t>(n)*n, {0,0});
    constexpr I SCALE = static_cast<I>(1000000000000LL);
    int i=0,j=0,z=0;
    while (input >> i >> j >> z) {
        if (i<0 || i>=n || j<i || j>=n) return 1;
        const I value=static_cast<I>(1000)*je*weights[i]*z*SCALE;
        upper[static_cast<size_t>(i)*n+j]={value,value};
    }
    for (int k=0;k<n;++k) {
        const I value=(static_cast<I>(1000)*jb*magnetic[k]-threshold)*weights[k]*SCALE;
        Interval& d=upper[static_cast<size_t>(k)*n+k];
        d.low+=value;
        d.high+=value;
    }

    int negative=0;
    for (int k=0;k<limit;++k) {
        const Interval pivot=upper[static_cast<size_t>(k)*n+k];
        if (pivot.low<=0 && pivot.high>=0) {
            std::cerr<<"FAIL|reason=uncertain_pivot|k="<<k
                     <<"|lower="<<decimal(pivot.low)
                     <<"|upper="<<decimal(pivot.high)<<"|json=0\n";
            return 2;
        }
        negative+=pivot.high<0;
        for (int a=k+1;a<n;++a) {
            const Interval x=upper[static_cast<size_t>(k)*n+a];
            if (x.low==0 && x.high==0) continue;
            for (int b=a;b<n;++b) {
                const Interval y=upper[static_cast<size_t>(k)*n+b];
                if (y.low==0 && y.high==0) continue;
                const Interval q=quotient(x,y,pivot);
                Interval& old=upper[static_cast<size_t>(a)*n+b];
                old.low-=q.high;
                old.high-=q.low;
                if (old.low>old.high) return 2;
            }
        }
    }
    std::cout << "HEBC-STURM|result=PARTIAL_PREFIX_CERTIFIED|JE="<<je
              <<"|JB="<<jb<<"|threshold="<<threshold
              <<"/1000|pivots_checked="<<limit<<"/"<<n
              <<"|negative_pivots_in_prefix="<<negative
              <<"|zero_ambiguous_pivots=0|remaining_pivots=UNCERTIFIED"
              <<"|arithmetic=I128_OUTWARD_INTERVAL|json=0\n";
}
