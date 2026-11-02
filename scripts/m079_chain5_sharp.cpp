// Exact chain-plus-five interval census. No third-party libraries.
// Work claim: https://github.com/Svyable/100/issues/254
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cstdio>
#include <numeric>
#include <string>
#include <vector>
using namespace std;
constexpr int K=5, FULL=(1<<K)-1, QMAX=40;
struct Interval {int a,b;};
using Intervals=array<Interval,K>;
struct Result {
    uint64_t extensions=0, best=0;
    array<uint64_t,10> pairs{};
    array<array<uint64_t,QMAX>,K> chain{};
};
int shifted_a[K], shifted_b[K], m;
bool valid(const Intervals &iv);
void prepare(const Intervals &iv) {
    int lo=iv[0].a,hi=iv[0].b;
    for(auto x:iv){lo=min(lo,x.a);hi=max(hi,x.b);}
    m=hi-lo;
    if(m>=QMAX) abort();
    for(int i=0;i<K;i++){shifted_a[i]=iv[i].a-lo;shifted_b[i]=iv[i].b-lo;}
}
Result sequential(const Intervals &iv) {
    if(!valid(iv))abort();
    prepare(iv);
    uint64_t F[QMAX][32]={},B[QMAX][32]={};
    F[0][0]=1;
    for(int q=0;q<=m;q++) for(int mask=0;mask<=FULL;mask++) {
        uint64_t f=F[q][mask];if(!f)continue;
        bool canchain=q<m;
        for(int i=0;i<K;i++)if(!(mask&(1<<i)) && shifted_b[i]<=q)canchain=false;
        if(canchain)F[q+1][mask]+=f;
        for(int i=0;i<K;i++)if(!(mask&(1<<i)) && shifted_a[i]<=q && q<=shifted_b[i])
            F[q][mask|(1<<i)]+=f;
    }
    B[m][FULL]=1;
    for(int q=m;q>=0;q--)for(int mask=FULL;mask>=0;mask--){
        if(q==m && mask==FULL)continue;
        bool canchain=q<m;
        for(int i=0;i<K;i++)if(!(mask&(1<<i)) && shifted_b[i]<=q)canchain=false;
        if(canchain)B[q][mask]+=B[q+1][mask];
        for(int i=0;i<K;i++)if(!(mask&(1<<i)) && shifted_a[i]<=q && q<=shifted_b[i])
            B[q][mask]+=B[q][mask|(1<<i)];
    }
    Result out;out.extensions=F[m][FULL];
    if(out.extensions!=B[0][0] || !out.extensions)abort();
    for(int q=0;q<=m;q++)for(int mask=0;mask<=FULL;mask++) {
        uint64_t f=F[q][mask];if(!f)continue;
        for(int i=0;i<K;i++)if(!(mask&(1<<i)) && shifted_a[i]<=q && q<=shifted_b[i]){
            uint64_t w=f*B[q][mask|(1<<i)];
            out.chain[i][q]+=w;
            for(int j=i+1;j<K;j++)if(!(mask&(1<<j)))
                out.pairs[i*(2*K-i-1)/2+j-i-1]+=w;
        }
    }
    for(auto v:out.pairs)out.best=max(out.best,min(v,out.extensions-v));
    for(int i=0;i<K;i++){
        uint64_t cumulative=0;
        for(int q=0;q<m;q++){
            cumulative+=out.chain[i][q];
            out.best=max(out.best,min(cumulative,out.extensions-cumulative));
        }
    }
    return out;
}
Result factorial_blocks(const Intervals &iv, bool mutate_tie=false) {
    if(!valid(iv))abort();
    prepare(iv);
    uint64_t F[QMAX+1][32]={},B[QMAX+1][32]={};
    constexpr int fac[6]={1,1,2,6,24,120};
    F[0][0]=1;
    for(int q=0;q<=m;q++)for(int mask=0;mask<=FULL;mask++){
        uint64_t f=F[q][mask];if(!f)continue;
        int elig=0,need=0;
        for(int i=0;i<K;i++)if(!(mask&(1<<i))){
            if(shifted_a[i]<=q && q<=shifted_b[i])elig|=1<<i;
            if(shifted_b[i]==q)need|=1<<i;
        }
        for(int T=elig;;T=(T-1)&elig){
            if((T&need)==need && (q<m || (mask|T)==FULL))
                F[q+1][mask|T]+=f*fac[__builtin_popcount((unsigned)T)];
            if(T==0)break;
        }
    }
    B[m+1][FULL]=1;
    for(int q=m;q>=0;q--)for(int mask=FULL;mask>=0;mask--){
        int elig=0,need=0;
        for(int i=0;i<K;i++)if(!(mask&(1<<i))){
            if(shifted_a[i]<=q && q<=shifted_b[i])elig|=1<<i;
            if(shifted_b[i]==q)need|=1<<i;
        }
        for(int T=elig;;T=(T-1)&elig){
            if((T&need)==need && (q<m || (mask|T)==FULL))
                B[q][mask]+=fac[__builtin_popcount((unsigned)T)]*B[q+1][mask|T];
            if(T==0)break;
        }
    }
    Result out;out.extensions=F[m+1][FULL];
    if(out.extensions!=B[0][0] || !out.extensions)abort();
    for(int q=0;q<=m;q++)for(int mask=0;mask<=FULL;mask++){
        uint64_t f=F[q][mask];if(!f)continue;
        int elig=0,need=0;
        for(int i=0;i<K;i++)if(!(mask&(1<<i))){
            if(shifted_a[i]<=q && q<=shifted_b[i])elig|=1<<i;
            if(shifted_b[i]==q)need|=1<<i;
        }
        for(int T=elig;;T=(T-1)&elig){
            if((T&need)==need && (q<m || (mask|T)==FULL)){
                int sz=__builtin_popcount((unsigned)T);
                uint64_t w=f*fac[sz]*B[q+1][mask|T];
                for(int i=0;i<K;i++)if(T&(1<<i)){
                    out.chain[i][q]+=w;
                    for(int j=i+1;j<K;j++)if(!(mask&(1<<j))){
                        int idx=i*(2*K-i-1)/2+j-i-1;
                        if(T&(1<<j)){
                            if(w%2)abort();
                            out.pairs[idx]+=mutate_tie?w:w/2;
                        }else out.pairs[idx]+=w;
                    }
                }
            }
            if(T==0)break;
        }
    }
    for(auto v:out.pairs)out.best=max(out.best,min(v,out.extensions-v));
    for(int i=0;i<K;i++){
        uint64_t cumulative=0;
        for(int q=0;q<m;q++){
            cumulative+=out.chain[i][q];
            out.best=max(out.best,min(cumulative,out.extensions-cumulative));
        }
    }
    return out;
}
bool valid(const Intervals &iv) {
    int maxa=-999,minb=999;
    for(auto x:iv){
        if(x.a>0 || x.b<0 || x.b-x.a<1)return false;
        maxa=max(maxa,x.a);minb=min(minb,x.b);
    }
    return maxa==0 && minb==0;
}
void print_instance(const Result &r){
    cout<<"E="<<r.extensions<<" best="<<r.best<<" delta="<<r.best<<"/"<<r.extensions<<"\n";
    cout<<"pairs=";
    for(auto x:r.pairs)cout<<x<<",";
    cout<<"\n";
    for(int i=0;i<K;i++){
        cout<<"gapweights"<<i<<"=";
        for(int q=0;q<=m;q++)cout<<r.chain[i][q]<<",";
        cout<<"\n";
    }
}
bool parse_instance(const string &s, Intervals &iv){
    stringstream ss(s);string token;
    int n=0,common_lo=-999,common_hi=999;
    while(getline(ss,token,',')){
        if(n>=K)return false;
        int a,b;char extra;
        if(sscanf(token.c_str(),"%d:%d%c",&a,&b,&extra)!=2)return false;
        iv[n++]={a,b};
        common_lo=max(common_lo,a);common_hi=min(common_hi,b);
    }
    if(n!=K || common_lo!=common_hi)return false;
    for(auto &x:iv){x.a-=common_lo;x.b-=common_lo;}
    return valid(iv);
}

/* New profile-sensitive gap atom bound:
   p_x(g) <= (1+S)/(L+S), S=sum_{y!=x}4/(L_y+3).
   If L>=5+4S then x has a 2/5-balanced chain pair.
   Duplicate outsider intervals imply a 1/2-balanced automorphism pair. */
bool symbolic_cut(const Intervals &iv) {
    for(int i=0;i<K;i++)for(int j=i+1;j<K;j++)
        if(iv[i].a==iv[j].a && iv[i].b==iv[j].b)return true;
    for(int i=0;i<K;i++){
        int L=iv[i].b-iv[i].a+1;
        if(L<5)continue;
        int64_t product=1,sum=0;
        for(int j=0;j<K;j++)if(i!=j)product*=iv[j].b-iv[j].a+4;
        for(int j=0;j<K;j++)if(i!=j)sum+=product/(iv[j].b-iv[j].a+4);
        if((L-5)*product>=16*sum)return true;
    }
    return false;
}
int main(int argc,char **argv){
    if(argc==3 && string(argv[1])=="--instance"){
        Intervals iv{};
        if(!parse_instance(argv[2],iv)){cerr<<"Invalid interval tuple\n";return 2;}
        Result a=sequential(iv),b=factorial_blocks(iv);
        if(a.extensions!=b.extensions || a.best!=b.best ||
           a.pairs!=b.pairs || a.chain!=b.chain){
            cerr<<"Independent recurrence mismatch\n";return 3;
        }
        cout<<"E="<<a.extensions<<" best="<<a.best<<"\n";
        return 0;
    }
    if(argc>2){cerr<<"Usage: checker [max_length<=15 | --instance a:b,...]\n";return 2;}
    int limit=argc>1?atoi(argv[1]):15;
    if(limit<2 || limit>15){cerr<<"Unsafe max_length\n";return 2;}
    vector<Interval> choices;
    for(int L=2;L<=limit;L++)for(int a=1-L;a<=0;a++)choices.push_back({a,a+L-1});
    sort(choices.begin(),choices.end(),[](Interval x,Interval y){
        return x.a!=y.a?x.a<y.a:x.b<y.b;
    });
    uint64_t checked=0,pruned=0,residual=0,bad=0,equals=0;
    uint64_t bestnum=1,bestden=1,hash=14695981039346656037ULL;
    auto add_hash=[&](const Intervals &iv,const Result &r){
        for(auto z:iv){
            hash^=uint64_t(z.a+64);hash*=1099511628211ULL;
            hash^=uint64_t(z.b+64);hash*=1099511628211ULL;
        }
        hash^=r.extensions;hash*=1099511628211ULL;
        hash^=r.best;hash*=1099511628211ULL;
    };
    size_t first_a0=0;
    while(first_a0<choices.size() && choices[first_a0].a<0)first_a0++;
    for(size_t i=0;i<choices.size();i++)
    for(size_t j=i;j<choices.size();j++)
    for(size_t k=j;k<choices.size();k++)
    for(size_t l=k;l<choices.size();l++){
        if(choices[i].b!=0 && choices[j].b!=0 &&
           choices[k].b!=0 && choices[l].b!=0)continue;
        for(size_t m=max(first_a0,l);m<choices.size();m++){
            Intervals iv={choices[i],choices[j],choices[k],choices[l],choices[m]};
            if(!valid(iv)){cerr<<"Enumeration scope error\n";return 3;}
            checked++;
            if(symbolic_cut(iv)){pruned++;continue;}
            residual++;
            Result a=sequential(iv),b=factorial_blocks(iv);
            if(a.extensions!=b.extensions || a.best!=b.best ||
               a.pairs!=b.pairs || a.chain!=b.chain){
                cerr<<"Dual DP mismatch at base case "<<checked<<"\n";return 3;
            }
            add_hash(iv,a);
            if(5*a.best<2*a.extensions){
                bad++;cerr<<"2/5 falsifier in base core\n";return 4;
            }
            if(5*a.best==2*a.extensions)equals++;
            if(a.best*bestden<bestnum*a.extensions){
                bestnum=a.best;bestden=a.extensions;
            }
        }
    }
    uint64_t extra=0,extra_bad=0,extra_num=1,extra_den=1;
    if(limit==15){
        vector<Interval> small;
        for(int L=2;L<=5;L++)for(int a=1-L;a<=0;a++)small.push_back({a,a+L-1});
        sort(small.begin(),small.end(),[](Interval x,Interval y){
            return x.a!=y.a?x.a<y.a:x.b<y.b;
        });
        for(int x=-15;x<=0;x++)
        for(size_t i=0;i<small.size();i++)
        for(size_t j=i+1;j<small.size();j++)
        for(size_t k=j+1;k<small.size();k++)
        for(size_t l=k+1;l<small.size();l++){
            Intervals iv={Interval{x,x+15},small[i],small[j],small[k],small[l]};
            if(!valid(iv) || symbolic_cut(iv))continue;
            extra++;
            Result a=sequential(iv),b=factorial_blocks(iv);
            if(a.extensions!=b.extensions || a.best!=b.best ||
               a.pairs!=b.pairs || a.chain!=b.chain){
                cerr<<"Dual DP mismatch in length-16 boundary\n";return 3;
            }
            add_hash(iv,a);
            if(5*a.best<2*a.extensions){
                extra_bad++;cerr<<"2/5 falsifier at length 16\n";return 4;
            }
            if(a.best*extra_den<extra_num*a.extensions){
                extra_num=a.best;extra_den=a.extensions;
            }
        }
    }
    cout<<"max_length="<<limit<<" checked="<<checked
        <<" pruned="<<pruned<<" residual="<<residual
        <<" bad="<<bad<<" equality_residual="<<equals
        <<" residual_min="<<bestnum<<"/"<<bestden
        <<" extra="<<extra<<" extra_bad="<<extra_bad
        <<" extra_min="<<extra_num<<"/"<<extra_den
        <<" digest="<<hex<<setw(16)<<setfill('0')<<hash<<dec<<"\n";
    return 0;
}
