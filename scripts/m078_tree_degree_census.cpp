// Independent labeled-Pruefer enumeration of card-degree signatures on trees n<=9.
// C++17, no graph packages; compares AHU canonical tree codes.
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;
using Graph=vector<vector<int>>;
string rooted(const Graph& g,int v,int parent){
  vector<string> a;
  for(int w:g[v])if(w!=parent)a.push_back(rooted(g,w,v));
  sort(a.begin(),a.end());string s="(";
  for(auto& x:a)s+=x;
  return s+")";
}
string canon(const Graph& g){
  int n=g.size();vector<int>d(n);for(int v=0;v<n;v++)d[v]=g[v].size();
  int remain=n;vector<int>layer;vector<bool> alive(n,true);
  while(remain>2){layer.clear();for(int v=0;v<n;v++)if(alive[v]&&d[v]==1)layer.push_back(v);
    for(int v:layer){alive[v]=false;remain--;for(int w:g[v])if(alive[w])d[w]--;}}
  vector<int> centers;for(int v=0;v<n;v++)if(alive[v])centers.push_back(v);
  if(centers.empty())centers.push_back(0);
  if(centers.size()==1)return rooted(g,centers[0],-1);
  string a=rooted(g,centers[0],centers[1]),b=rooted(g,centers[1],centers[0]);
  if(a>b)swap(a,b);
  return "("+a+b+")";
}
string sig(const Graph& g){
  int n=g.size();vector<string> cards;
  for(int v=0;v<n;v++){
    string s;for(int w=0;w<n;w++)if(w!=v){int d=g[w].size();for(int x:g[w])if(x==v){d--;break;}s.push_back(char('0'+d));}
    sort(s.begin(),s.end());cards.push_back(s);
  }
  sort(cards.begin(),cards.end());string result;
  for(auto& s:cards){result+=s;result+='|';}
  return result;
}
Graph from_pruefer(const vector<int>& a,int n){
  Graph g(n);vector<int>d(n,1);for(int x:a)d[x]++;
  for(int x:a){int leaf=0;while(d[leaf]!=1)leaf++;
    g[leaf].push_back(x);g[x].push_back(leaf);d[leaf]--;d[x]--;}
  int u=-1,v=-1;for(int i=0;i<n;i++)if(d[i]==1){if(u<0)u=i;else v=i;}
  g[u].push_back(v);g[v].push_back(u);return g;
}
int main(int argc,char**argv){
  int max_n=(argc>1?stoi(argv[1]):9);
  if(max_n<3||max_n>9){cerr<<"max_n must be in [3,9]\n";return 2;}
  for(int n=3;n<=max_n;n++){
    long long total=1;for(int i=0;i<n-2;i++)total*=n;
    map<string,string> first;set<string> iso;
    vector<int>a(n-2);
    for(long long code=0;code<total;code++){
      long long z=code;for(int i=0;i<n-2;i++){a[i]=z%n;z/=n;}
      Graph g=from_pruefer(a,n);
      string c=canon(g),s=sig(g);iso.insert(c);
      auto it=first.find(s);
      if(it!=first.end()&&it->second!=c){cerr<<"COLLISION n="<<n<<" code="<<code<<"\n";return 1;}
      first.emplace(s,c);
    }
    cout<<"n="<<n<<" labeled="<<total<<" isomorphism_types="<<iso.size()<<" card_degree_signatures="<<first.size()<<" collision=0\n";
  }
}
