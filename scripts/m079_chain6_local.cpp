// M079 six-antichain-outsider sharp local census. C++17, integer arithmetic only.
// See research/M079_CHAIN6_LOCAL_SHARP.md for the completeness argument and limitations.
#include <bits/stdc++.h>
using namespace std;
using ll=long long;
using i128=__int128_t;
struct I { int a,b; };
struct Result { ll E,best; int type,i,j; };

// Sequential one-element order-ideal recurrence, plus all pair numerators.
Result calc(const vector<I>& intervals) {
 const int k=intervals.size(),N=1<<k,full=N-1;
 int left=1000,right=-1000;
 for(auto v:intervals){left=min(left,v.a);right=max(right,v.b);}
 int m=right-left;
 if(m>80)return {0,0,0,0,0};
 vector<array<ll,64>> F(m+1),B(m+1);
 F[0][0]=1;
 int A[6],Z[6];
 for(int i=0;i<k;i++){A[i]=intervals[i].a-left;Z[i]=intervals[i].b-left;}
 for(int q=0;q<=m;q++)for(int mask=0;mask<N;mask++){
  ll v=F[q][mask];if(!v)continue;
  for(int i=0;i<k;i++)if(!(mask>>i&1)&&A[i]<=q&&q<=Z[i])F[q][mask|(1<<i)]+=v;
  if(q<m){
   bool ok=true;
   for(int i=0;i<k;i++)if(!(mask>>i&1)&&Z[i]<=q){ok=false;break;}
   if(ok)F[q+1][mask]+=v;
  }
 }
 B[m][full]=1;
 for(int q=m;q>=0;q--)for(int mask=full;mask>=0;mask--){
  if(q==m&&mask==full)continue;
  ll v=0;
  for(int i=0;i<k;i++)if(!(mask>>i&1)&&A[i]<=q&&q<=Z[i])v+=B[q][mask|(1<<i)];
  if(q<m){
   bool ok=true;
   for(int i=0;i<k;i++)if(!(mask>>i&1)&&Z[i]<=q){ok=false;break;}
   if(ok)v+=B[q+1][mask];
  }
  B[q][mask]=v;
 }
 ll E=F[m][full];
 if(E!=B[0][0]){cerr<<"DP mismatch"<<endl;exit(1);}
 if(E<=0)return {0,0,0,0,0};
 ll pairs[6][6]={},marg[6][81]={};
 for(int q=0;q<=m;q++)for(int mask=0;mask<N;mask++){
  ll f=F[q][mask];if(!f)continue;
  for(int i=0;i<k;i++)if(!(mask>>i&1)&&A[i]<=q&&q<=Z[i]){
   ll w=f*B[q][mask|(1<<i)];
   marg[i][q]+=w;
   for(int j=0;j<k;j++)if(i!=j&&!(mask>>j&1))pairs[i][j]+=w;
  }
 }
 ll best=0;int type=0,bi=-1,bj=-1;
 for(int i=0;i<k;i++){
  for(int j=i+1;j<k;j++){
   ll x=min(pairs[i][j],E-pairs[i][j]);
   if(x>best){best=x;type=0;bi=i;bj=j;}
  }
  ll acc=0;
  for(int q=0;q<m;q++){
   acc+=marg[i][q];
   ll x=min(acc,E-acc);
   if(x>best){best=x;type=1;bi=i;bj=q+1+left;}
  }
 }
 return {E,best,type,bi,bj};
}

// Independently structured factorial gap-block recurrence.
// A block T contributes |T|! orders; two members share each order equally.
Result calc_blocks(const vector<I>& intervals){
 const int k=intervals.size(),N=1<<k,full=N-1;
 int left=1000,right=-1000;
 for(auto v:intervals){left=min(left,v.a);right=max(right,v.b);}
 int m=right-left;
 vector<array<ll,64>> F(m+2),B(m+2);
 F[0][0]=1;B[m+1][full]=1;
 int A[6],Z[6];
 for(int i=0;i<k;i++){A[i]=intervals[i].a-left;Z[i]=intervals[i].b-left;}
 int fact[]={1,1,2,6,24,120,720};
 auto visit=[&](int q,int mask,auto cb){
  int avail=0,forced=0;
  for(int i=0;i<k;i++)if(!(mask>>i&1)){
   if(A[i]<=q&&q<=Z[i])avail|=1<<i;
   if(Z[i]<=q)forced|=1<<i;
  }
  if(forced&~avail)return;
  for(int sub=avail;;sub=(sub-1)&avail){
   if((sub&forced)==forced)cb(sub,fact[__builtin_popcount((unsigned)sub)]);
   if(sub==0)break;
  }
 };
 for(int q=0;q<=m;q++)for(int mask=0;mask<N;mask++){
  ll f=F[q][mask];if(!f)continue;
  visit(q,mask,[&](int sub,int weight){F[q+1][mask|sub]+=f*weight;});
 }
 for(int q=m;q>=0;q--)for(int mask=0;mask<N;mask++){
  ll v=0;
  visit(q,mask,[&](int sub,int weight){v+=(ll)weight*B[q+1][mask|sub];});
  B[q][mask]=v;
 }
 ll E=F[m+1][full];
 if(E!=B[0][0]){cerr<<"block mismatch"<<endl;exit(1);}
 ll pairs[6][6]={},marg[6][81]={};
 for(int q=0;q<=m;q++)for(int mask=0;mask<N;mask++){
  ll f=F[q][mask];if(!f)continue;
  visit(q,mask,[&](int sub,int weight){
   ll w=f*weight*B[q+1][mask|sub];if(!w)return;
   for(int i=0;i<k;i++)if(sub>>i&1){
    marg[i][q]+=w;
    for(int j=0;j<k;j++)if(i!=j&&!(mask>>j&1)){
     if(sub>>j&1)pairs[i][j]+=w/2;
     else pairs[i][j]+=w;
    }
   }
  });
 }
 ll best=0;int type=0,bi=-1,bj=-1;
 for(int i=0;i<k;i++){
  for(int j=i+1;j<k;j++){
   ll x=min(pairs[i][j],E-pairs[i][j]);
   if(x>best){best=x;type=0;bi=i;bj=j;}
  }
  ll acc=0;
  for(int q=0;q<m;q++){
   acc+=marg[i][q];
   ll x=min(acc,E-acc);
   if(x>best){best=x;type=1;bi=i;bj=q+1+left;}
  }
 }
 return {E,best,type,bi,bj};
}

int main(int argc,char**argv){
 int L=8;bool check=false;string instance="";
 for(int i=1;i<argc;i++){
  string arg=argv[i];
  if(arg=="--check")check=true;
  else if(arg=="--max-length"&&i+1<argc)L=stoi(argv[++i]);
  else if(arg=="--instance"&&i+1<argc)instance=argv[++i];
  else {cerr<<"Usage: m079_chain6_local [--check] [--max-length 4..8] [--instance a:b,...]"<<endl;return 2;}
 }
 if(!instance.empty()){
  vector<I> v;stringstream ss(instance);string token;
  while(getline(ss,token,',')){
   auto p=token.find(':');
   if(p==string::npos){cerr<<"Bad interval"<<endl;return 2;}
   v.push_back({stoi(token.substr(0,p)),stoi(token.substr(p+1))});
  }
  if(v.size()!=6){cerr<<"Need six intervals"<<endl;return 2;}
  int ma=-999,mb=999,left=999,right=-999;
  for(auto x:v){
   ma=max(ma,x.a);mb=min(mb,x.b);
   left=min(left,x.a);right=max(right,x.b);
   if(x.a>x.b||x.a>0||x.b<0||x.b-x.a+1<2){cerr<<"Invalid interval"<<endl;return 2;}
  }
  if(ma!=0||mb!=0||right-left>80){cerr<<"Invalid common gap or chain length"<<endl;return 2;}
  auto r=calc(v),rr=calc_blocks(v);
  if(r.E!=rr.E||r.best!=rr.best){cerr<<"Independent recurrence mismatch"<<endl;return 3;}
  cout<<"INSTANCE E="<<r.E<<" best="<<r.best<<"/"<<r.E<<" type="<<r.type<<" pair="<<r.i<<","<<r.j<<endl;
  if(check&&!(r.E==60060&&r.best==25840))return 4;
  return 0;
 }
 if(L<4||L>8){cerr<<"Supported exact census lengths: 4..8"<<endl;return 2;}
 vector<I> options;
 for(int len=2;len<=L;len++)for(int a=1-len;a<=0;a++)options.push_back({a,a+len-1});
 vector<I> v;Result best{1,1,0,0,0};
 long long n=0,equals=0,sharp=0;
 unsigned long long digest=14695981039346656037ULL;
 function<void(int)> dfs=[&](int start){
  if(v.size()==6){
   int ma=-999,mb=999;
   for(auto x:v){ma=max(ma,x.a);mb=min(mb,x.b);}
   if(ma!=0||mb!=0)return;
   n++;auto r=calc(v);
   for(auto x:v)for(int z:{x.a,x.b}){
    unsigned long long y=(unsigned long long)(z+100);
    for(int t=0;t<2;t++){digest^=(y>>(8*t))&255;digest*=1099511628211ULL;}
   }
   for(ll z:{r.E,r.best}){
    unsigned long long y=(unsigned long long)z;
    for(int t=0;t<8;t++){digest^=(y>>(8*t))&255;digest*=1099511628211ULL;}
   }
   if(n%97==0){
    auto rr=calc_blocks(v);
    if(r.E!=rr.E||r.best!=rr.best){cerr<<"Independent recurrence mismatch at "<<n<<endl;exit(3);}
   }
   if(r.E<=0){cerr<<"No linear extensions"<<endl;exit(3);}
   if((i128)r.best*best.E<(i128)best.best*r.E){
    best=r;equals=1;
    cout<<"BEST "<<n<<" "<<r.best<<"/"<<r.E<<" : ";
    for(auto x:v)cout<<"["<<x.a<<","<<x.b<<"]";cout<<endl;
   }else if((i128)r.best*best.E==(i128)best.best*r.E)equals++;
   if((i128)r.best*3003==(i128)1292*r.E){
    sharp++;
    cout<<"SHARP "<<n<<" "<<r.best<<"/"<<r.E<<" : ";
    for(auto x:v)cout<<"["<<x.a<<","<<x.b<<"]";cout<<endl;
   }
   return;
  }
  for(int j=start;j<=(int)options.size()-(6-(int)v.size());j++){
   v.push_back(options[j]);dfs(j+1);v.pop_back();
  }
 };
 dfs(0);
 cout<<"FINAL L="<<L<<" crosschecks="<<n/97<<" count="<<n
     <<" best="<<best.best<<"/"<<best.E<<" equality="<<equals
     <<" sharp="<<sharp<<" digest="<<hex<<digest<<dec<<endl;
 if(check){
  if(L==8&&(n!=923944||best.best*3003!=best.E*1292||equals!=2||sharp!=2||digest!=0x9a36908f323ec1f1ULL))return 4;
  if(L==4&&(n!=82||digest!=0x7c4fb13ad7fec712ULL))return 4;
 }
 return 0;
}
