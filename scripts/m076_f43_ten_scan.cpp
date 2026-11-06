// Exact ten-deletion superset scanner for M076.
// Input: minimal cover masks and candidate forbidden-edge graphs.
// Every ten-set containing a listed minimal cover is generated, with
// multiplicity. Output: MASK lines for individual capacity >=5, followed
// by a SUMMARY line. Python independently reconstructs and checks all
// mathematical inputs and the high-capacity output.
#include <vector>
#include <fstream>
#include <iostream>
#include <cstdint>
#include <utility>

using namespace std;
using U=uint64_t;
struct Cand{vector<U> e; U super;};
vector<Cand> cands; vector<U> mins;
U counts[20]={}; unsigned long long visited=0, high=0;
ostream &out=cout;
void inspect(U d){
 ++visited;
 int cap=0;
 for(int i=0;i<(int)cands.size();++i){
  auto &c=cands[i];
  bool good=true;
  for(U edge:c.e) if(!(edge&d)){good=false;break;}
  if(good) cap+= (i>=162&&i<270&&!(c.super & ~d))?2:1;
 }
 if(cap<20)counts[cap]++;
 if(cap>=5){++high;out<<d<<" "<<cap<<"\n";}
}
void ext(const vector<int>& free, int from, int left,U d){
 if(!left){inspect(d);return;}
 for(int j=from;j<=(int)free.size()-left;j++)ext(free,j+1,left-1,d|(U(1)<<free[j]));
}
int main(){
 istream &in=cin;
 int m;in>>m;
 for(int i=0;i<m;i++){U d;in>>d;mins.push_back(d);}
 int n;in>>n;
 for(int i=0;i<n;i++){
  int cnt;U super;in>>cnt>>super;Cand c;c.super=super;
  for(int j=0;j<cnt;j++){U e;in>>e;c.e.push_back(e);}
  cands.push_back(std::move(c));
 }

 for(int k=0;k<m;k++){
  U d=mins[k];vector<int> free;
  for(int i=0;i<54;i++)if(!(d&(U(1)<<i)))free.push_back(i);
  ext(free,0,10-__builtin_popcountll(d),d);

 }

 out<<"SUMMARY "<<visited<<" "<<high;
 for(int i=0;i<20;i++)out<<" "<<counts[i];
 out<<"\n";
}
