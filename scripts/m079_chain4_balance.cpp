// Exact M079 chain-plus-four census, C++17, no external dependencies.
// Two distinct counters: sequential order-ideal paths and factorial gap blocks.
// Run: c++ -O3 -std=c++17 scripts/m079_chain4_balance.cpp -o /tmp/m079_chain4
//      /tmp/m079_chain4 18 --transcript | shasum -a 256
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
using i64 = int64_t;
struct Interval {int a,b;};
struct Counts {
    i64 E=0, pair[4][4]={}, chain[4][64]={};
    int m=0;
    i64 best() const {
        i64 b=0;
        for(int x=0;x<4;x++){
            for(int y=x+1;y<4;y++)b=max(b,min(pair[x][y],E-pair[x][y]));
            for(int q=0;q<m;q++)b=max(b,min(chain[x][q],E-chain[x][q]));
        }
        return b;
    }
    bool same(const Counts& t) const {
        if(E!=t.E||m!=t.m)return false;
        for(int x=0;x<4;x++){
            for(int y=x+1;y<4;y++)if(pair[x][y]!=t.pair[x][y])return false;
            for(int q=0;q<m;q++)if(chain[x][q]!=t.chain[x][q])return false;
        }
        return true;
    }
};
Counts sequential(const array<Interval,4>& iv){
    int lo=0,hi=0;for(auto z:iv){lo=min(lo,z.a);hi=max(hi,z.b);}
    int m=hi-lo;if(m>=64){cerr<<"too many gaps\n";exit(2);}
    int a[4],b[4];for(int i=0;i<4;i++){a[i]=iv[i].a-lo;b[i]=iv[i].b-lo;}
    i64 F[64][16]={},B[64][16]={};F[0][0]=1;
    for(int q=0;q<=m;q++)for(int mask=0;mask<16;mask++){
        i64 f=F[q][mask];if(!f)continue;
        if(q<m){bool legal=true;for(int i=0;i<4;i++)if(!(mask>>i&1)&&b[i]<=q){legal=false;break;}
            if(legal)F[q+1][mask]+=f;}
        for(int i=0;i<4;i++)if(!(mask>>i&1)&&a[i]<=q&&q<=b[i])F[q][mask|(1<<i)]+=f;
    }
    B[m][15]=1;
    for(int q=m;q>=0;q--)for(int mask=15;mask>=0;mask--){
        if(q==m&&mask==15)continue;
        i64 s=0;
        if(q<m){bool legal=true;for(int i=0;i<4;i++)if(!(mask>>i&1)&&b[i]<=q){legal=false;break;}
            if(legal)s+=B[q+1][mask];}
        for(int i=0;i<4;i++)if(!(mask>>i&1)&&a[i]<=q&&q<=b[i])s+=B[q][mask|(1<<i)];
        B[q][mask]=s;
    }
    Counts out;out.E=F[m][15];out.m=m;
    for(int q=0;q<=m;q++)for(int mask=0;mask<16;mask++){
        i64 f=F[q][mask];if(!f)continue;
        for(int x=0;x<4;x++)if(!(mask>>x&1)&&a[x]<=q&&q<=b[x]){
            i64 ways=f*B[q][mask|(1<<x)];
            for(int y=x+1;y<4;y++)if(!(mask>>y&1))out.pair[x][y]+=ways;
            for(int c=q;c<m;c++)out.chain[x][c]+=ways;
        }
    }
    return out;
}
Counts gap_blocks(const array<Interval,4>& iv){
    int lo=0,hi=0;for(auto z:iv){lo=min(lo,z.a);hi=max(hi,z.b);}
    int m=hi-lo;if(m>=63){cerr<<"too many gaps\n";exit(2);}
    int elig[64]={};
    for(int q=0;q<=m;q++)for(int i=0;i<4;i++)if(iv[i].a<=q+lo&&q+lo<=iv[i].b)elig[q]|=1<<i;
    constexpr i64 fact[5]={1,1,2,6,24};
    i64 F[65][16]={},B[65][16]={};F[0][0]=1;
    for(int q=0;q<=m;q++)for(int mask=0;mask<16;mask++){
        i64 f=F[q][mask];if(!f)continue;
        int remaining=elig[q]&~mask;
        for(int t=remaining;;t=(t-1)&remaining){
            F[q+1][mask|t]+=f*fact[__builtin_popcount((unsigned)t)];
            if(t==0)break;
        }
    }
    B[m+1][15]=1;
    for(int q=m;q>=0;q--)for(int mask=0;mask<16;mask++){
        int remaining=elig[q]&~mask;i64 s=0;
        for(int t=remaining;;t=(t-1)&remaining){
            s+=fact[__builtin_popcount((unsigned)t)]*B[q+1][mask|t];
            if(t==0)break;
        }
        B[q][mask]=s;
    }
    Counts out;out.E=F[m+1][15];out.m=m;
    for(int q=0;q<=m;q++)for(int mask=0;mask<16;mask++){
        i64 f=F[q][mask];if(!f)continue;
        int remaining=elig[q]&~mask;
        for(int t=remaining;;t=(t-1)&remaining){
            if(t){
                i64 suffix=B[q+1][mask|t];
                i64 ways=f*fact[__builtin_popcount((unsigned)t)]*suffix;
                for(int x=0;x<4;x++)if(t>>x&1){
                    for(int c=q;c<m;c++)out.chain[x][c]+=ways;
                    for(int y=x+1;y<4;y++)if(!(mask>>y&1)){
                        if(t>>y&1)out.pair[x][y]+=ways/2;
                        else out.pair[x][y]+=ways;
                    }
                }
            }
            if(t==0)break;
        }
    }
    return out;
}
int main(int argc,char**argv){
    int L=argc>1?atoi(argv[1]):18;
    bool transcript=argc>2&&string(argv[2])=="--transcript";
    if(L<2||L>30){cerr<<"length must be 2..30\n";return 2;}
    vector<Interval> opts;
    for(int len=2;len<=L;len++)for(int a=1-len;a<=0;a++)opts.push_back({a,a+len-1});
    int N=opts.size();
    i64 cases=0,sharp=0,num=1,den=2;array<Interval,4> witness{};
    auto start=chrono::steady_clock::now();
    for(int i=0;i<N;i++)for(int j=i;j<N;j++)for(int k=j;k<N;k++)for(int l=k;l<N;l++){
        array<Interval,4> iv={opts[i],opts[j],opts[k],opts[l]};
        int left=-100,right=100;
        for(auto z:iv){left=max(left,z.a);right=min(right,z.b);}
        if(left!=0||right!=0)continue;
        Counts a=sequential(iv),b=gap_blocks(iv);
        if(!a.same(b)||a.E<=0){
            cerr<<"INDEPENDENT COUNTER DISAGREEMENT: ";
            for(auto z:iv)cerr<<"["<<z.a<<","<<z.b<<"]";
            cerr<<" sequential="<<a.E<<","<<a.best()<<" gap-blocks="<<b.E<<","<<b.best()<<"\n";return 1;
        }
        i64 best=a.best();cases++;
        if(best*den<num*a.E){num=best;den=a.E;witness=iv;}
        if(best*61==25*a.E)sharp++;
        if(best*61<25*a.E){cerr<<"BOUND FALSE\n";return 1;}
        if(transcript){
            for(auto z:iv)cout<<z.a<<","<<z.b<<";";
            cout<<a.E<<","<<best<<"\n";
        }
    }
    double secs=chrono::duration<double>(chrono::steady_clock::now()-start).count();
    cerr<<"length="<<L<<" cases="<<cases<<" min="<<num<<"/"<<den<<" sharp="<<sharp<<" seconds="<<secs<<" witness=";
    for(auto z:witness)cerr<<"["<<z.a<<","<<z.b<<"]";
    cerr<<"\n";
    return 0;
}
