#include <array>
#include <vector>
#include <set>
#include <algorithm>
#include <iostream>
#include <cstdint>
using namespace std;
using M=uint32_t;
M m(initializer_list<int> s){M v=0;for(int x:s)v|=(M(1)<<x);return v;}
bool sun(M a,M b,M c){return (a&b)==(a&c) && (a&b)==(b&c);}
int main(){
 vector<M> F;
 for(int offset: {0,9}) for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)
 for(int a=0;a<3;a++)for(int b=a+1;b<3;b++)
 for(int c=0;c<3;c++)for(int d=c+1;d<3;d++)
 F.push_back(m({offset+3*i+a,offset+3*i+b,offset+3*j+c,offset+3*j+d}));
 set<int> D={0,2,3,5,6,8,18,24,25,26};
 vector<M> I={m({0,1,3,18}),m({0,2,3,18}),m({1,2,3,18}),m({3,6,7,18}),m({5,6,7,18})};
 set<M> forbidden(F.begin(),F.end());for(auto x:I)forbidden.insert(x);
 vector<pair<int,array<int,4>>> result;
 // Independent all-triples baseline check, not relying on Python's verifier.
 vector<M> baseline=I;
 for(int i=0;i<54;i++)if(!D.count(i))baseline.push_back(F[i]);
 for(size_t i=0;i<baseline.size();i++)
   for(size_t j=0;j<i;j++)for(size_t k=0;k<j;k++)
     if(sun(baseline[i],baseline[j],baseline[k]))return 2;
 long long tested=0;
 for(int drop=0;drop<54;drop++)if(!D.count(drop)){
   vector<M> kept=I;
   for(int i=0;i<54;i++)if(!D.count(i)&&i!=drop)kept.push_back(F[i]);
   for(int a=0;a<23;a++)for(int b=a+1;b<23;b++)for(int c=b+1;c<23;c++)for(int d=c+1;d<23;d++){
      M x=m({a,b,c,d});if(forbidden.count(x))continue;tested++;
      bool ok=true;
      for(size_t i=0;i<kept.size() && ok;i++)for(size_t j=0;j<i;j++)
        if(sun(kept[i],kept[j],x)){ok=false;break;}
      if(ok){
        // Direct literal replay for each positive solution.
        for(size_t i=0;i<kept.size();i++)for(size_t j=0;j<i;j++)
          if(sun(kept[i],kept[j],x))return 3;
        result.push_back({drop,{a,b,c,d}});
      }
   }
 }
 cout<<"tested "<<tested<<" solutions "<<result.size()<<"\n";
 for(auto const& [drop,a]:result)cout<<drop<<" "<<a[0]<<" "<<a[1]<<" "<<a[2]<<" "<<a[3]<<"\n";
 // Second direct sweep: classify all individually insertable candidates
 // after the fixed eleven deletions, with no prior insertions assumed.
 set<int> D11=D;D11.insert(19);
 vector<M> old11;
 for(int i=0;i<54;i++)if(!D11.count(i))old11.push_back(F[i]);
 vector<array<int,4>> allowed;
 for(int a=0;a<23;a++)for(int b=a+1;b<23;b++)
 for(int c=b+1;c<23;c++)for(int d=c+1;d<23;d++){
   M x=m({a,b,c,d});
   if(find(F.begin(),F.end(),x)!=F.end())continue;
   bool ok=true;
   for(size_t i=0;i<old11.size()&&ok;i++)
     for(size_t j=0;j<i;j++)
       if(sun(old11[i],old11[j],x)){ok=false;break;}
   if(ok)allowed.push_back({a,b,c,d});
 }
 cout<<"allowed "<<allowed.size()<<"\n";
 for(auto const& a:allowed)
   cout<<"A "<<a[0]<<" "<<a[1]<<" "<<a[2]<<" "<<a[3]<<"\n";
}
