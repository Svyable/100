// Exact chain-plus-five interval census. No third-party libraries.
// Work claim: https://github.com/Svyable/100/issues/201
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
int main(int argc,char **argv){
    int limit=15;bool dual=false,transcript=false,witness=false,mutate_tie=false;
    string instance;
    for(int i=1;i<argc;i++){
        string s=argv[i];
        if(s=="--dual")dual=true;
        else if(s=="--transcript")transcript=true;
        else if(s=="--witness")witness=true;
        else if(s=="--mutate-tie")mutate_tie=true;
        else if(s=="--instance" && i+1<argc)instance=argv[++i];
        else if(s=="--max-length" && i+1<argc)limit=atoi(argv[++i]);
        else {cerr<<"Unknown option "<<s<<"\n";return 2;}
    }
    if(limit<2 || limit>15 || (witness && !instance.empty()) ||
       (mutate_tie && !witness && instance.empty())){
        cerr<<"Invalid or unsafe command-line scope\n";return 2;
    }
    if(witness || !instance.empty()){
        Intervals iv{};
        if(witness)iv={{{-4,0},{-1,0},{-1,1},{0,1},{0,4}}};
        else if(!parse_instance(instance,iv)){
            cerr<<"Invalid interval tuple: requires five intervals of length >=2 and unique common gap\n";
            return 2;
        }
        Result a=sequential(iv),b=factorial_blocks(iv,mutate_tie);
        if(a.extensions!=b.extensions || a.best!=b.best || a.pairs!=b.pairs || a.chain!=b.chain){
            cerr<<"Independent recurrence mismatch (mutation detected if requested)\n";return 3;
        }
        print_instance(a);
        return 0;
    }
    vector<Interval> choices;
    for(int L=2;L<=limit;L++)for(int a=1-L;a<=0;a++)choices.push_back({a,a+L-1});
    sort(choices.begin(),choices.end(),[](auto x,auto y){return x.a!=y.a?x.a<y.a:x.b<y.b;});
    uint64_t cases=0,sharp=0,negative=0,dual_checked=0;
    uint64_t bestnum=1,bestden=1;
    uint64_t fnv=14695981039346656037ULL;
    auto add_hash=[&](uint64_t n){
        for(int i=0;i<8;i++){
            fnv^=(n>>(8*i))&255;
            fnv*=1099511628211ULL;
        }
    };
    Intervals bestiv{};
    for(size_t a=0;a<choices.size();a++)
    for(size_t b=a;b<choices.size();b++)
    for(size_t c=b;c<choices.size();c++)
    for(size_t d=c;d<choices.size();d++)
    for(size_t e=d;e<choices.size();e++){
        Intervals iv={choices[a],choices[b],choices[c],choices[d],choices[e]};
        if(!valid(iv))continue;
        Result x=sequential(iv);cases++;
        if(dual){
            Result y=factorial_blocks(iv);dual_checked++;
            if(x.extensions!=y.extensions || x.best!=y.best || x.pairs!=y.pairs || x.chain!=y.chain){
                cerr<<"MISMATCH at "<<cases<<"\n";return 3;
            }
        }
        if(8*x.best<3*x.extensions){negative++;cerr<<"3/8 FALSIFIER at "<<cases<<"\n";return 4;}
        if(x.best*bestden<bestnum*x.extensions){
            bestnum=x.best;bestden=x.extensions;bestiv=iv;sharp=1;
        }else if(x.best*bestden==bestnum*x.extensions)sharp++;
        for(auto z:iv){add_hash(uint64_t(z.a+64));add_hash(uint64_t(z.b+64));}
        add_hash(x.extensions);add_hash(x.best);
        if(transcript){
            for(auto z:iv)cout<<z.a<<","<<z.b<<";";
            cout<<" E="<<x.extensions<<" B="<<x.best<<"\n";
        }
    }
    cerr<<"cases="<<cases<<" dual="<<dual_checked<<" negative="<<negative
        <<" minimum="<<bestnum<<"/"<<bestden<<" multiplicity="<<sharp
        <<" max_length="<<limit<<" intervals="<<choices.size()<<" fnv64="
        <<hex<<setw(16)<<setfill('0')<<fnv<<dec<<" witness=";
    for(auto z:bestiv)cerr<<"["<<z.a<<","<<z.b<<"]";
    cerr<<"\n";
    return 0;
}
