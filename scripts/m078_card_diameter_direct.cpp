// Independent C++17 literal-card audit for X-M078-CARD-DIAMETER.
// c++ -O3 -std=c++17 scripts/m078_card_diameter_direct.cpp -o /tmp/m078_cd && /tmp/m078_cd
#include <algorithm>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <utility>
#include <vector>
using namespace std;
using Graph=vector<vector<int>>;
Graph build(int k,int n,int v){
  if(k<3||n<16*k||v<0||v>1)throw invalid_argument("parameters");
  int L=2*k-3,h=L+4,A=2*h-1+(n-16*k)/3,t=(n-16*k)%3;
  int lengths[3][2][2]={{{L,L+2},{L+1,L+1}},
                         {{L,L+3},{L+1,L+2}},
                         {{L+1,L+3},{L+2,L+2}}};
  Graph g(n);int next=1,mark[2]={0,0};
  auto add=[&](int a,int b){g[a].push_back(b);g[b].push_back(a);};
  for(int arm=0;arm<3;arm++){
    int p=0;
    for(int d=1;d<=A;d++){
      int q=next++;add(p,q);p=q;
      if(arm<2&&d==h)mark[arm]=q;
    }
  }
  for(int arm=0;arm<2;arm++){
    int p=mark[arm];
    for(int d=0;d<lengths[t][v][arm];d++){int q=next++;add(p,q);p=q;}
  }
  if(next!=n)throw logic_error("order");
  return g;
}
int card_diameter(const Graph&g,int omit){
  int n=g.size(),result=0;vector<bool> seen(n);seen[omit]=true;
  auto bfs=[&](int start){
    vector<int> dist(n,-1);queue<int> q;q.push(start);dist[start]=0;int far=start;
    while(!q.empty()){
      int u=q.front();q.pop();if(dist[u]>dist[far])far=u;
      for(int w:g[u])if(w!=omit&&dist[w]<0){dist[w]=dist[u]+1;q.push(w);}
    }
    return make_pair(far,dist);
  };
  for(int u=0;u<n;u++)if(!seen[u]){
    auto [a,comp]=bfs(u);
    for(int j=0;j<n;j++)if(comp[j]>=0)seen[j]=true;
    auto [b,d]=bfs(a);result=max(result,d[b]);
  }
  return result;
}
vector<int> canon(int t){
  vector<pair<int,int>> edges;
  for(int i=0;i<t;i++)for(int j=i+1;j<t;j++)edges.push_back({i,j});
  int m=edges.size();vector<int> perm(t);iota(perm.begin(),perm.end(),0);
  vector<int> table(1<<m,(1<<m)-1);
  do{
    vector<int> transform(m);
    for(int z=0;z<m;z++){
      int a=perm[edges[z].first],b=perm[edges[z].second];
      if(a>b)swap(a,b);
      transform[z]=find(edges.begin(),edges.end(),make_pair(a,b))-edges.begin();
    }
    for(int mask=0;mask<(1<<m);mask++){
      int newmask=0;
      for(int z=0;z<m;z++)if(mask>>z&1)newmask|=1<<transform[z];
      table[mask]=min(table[mask],newmask);
    }
  }while(next_permutation(perm.begin(),perm.end()));
  return table;
}
using Card=vector<long long>;
map<Card,int> signature(const Graph&g,int k){
  int n=g.size(),dim=0;
  vector<vector<int>> canonical(k+1);
  vector<int> offset(k+1);
  for(int t=1;t<=k;t++){
    canonical[t]=canon(t);offset[t]=dim;dim+=canonical[t].size();
  }
  vector<vector<bool>> adj(n,vector<bool>(n));
  for(int u=0;u<n;u++)for(int v:g[u])adj[u][v]=true;
  map<Card,int> output;
  for(int omit=0;omit<n;omit++){
    vector<int> vs;for(int u=0;u<n;u++)if(u!=omit)vs.push_back(u);
    Card count(dim,0);int a[4];
    auto count_subset=[&](int t){
      int mask=0,bit=0;
      for(int i=0;i<t;i++)for(int j=i+1;j<t;j++){
        if(adj[a[i]][a[j]])mask|=1<<bit;
        bit++;
      }
      count[offset[t]+canonical[t][mask]]++;
    };
    for(int i=0;i<n-1;i++){
      a[0]=vs[i];count_subset(1);
      for(int j=i+1;j<n-1;j++){
        a[1]=vs[j];count_subset(2);
        for(int p=j+1;p<n-1;p++){
          a[2]=vs[p];count_subset(3);
          if(k>=4)for(int q=p+1;q<n-1;q++){
            a[3]=vs[q];count_subset(4);
          }
        }
      }
    }
    vector<int> degrees;
    for(int u=0;u<n;u++)if(u!=omit)
      degrees.push_back((int)g[u].size()-(int)adj[u][omit]);
    sort(degrees.begin(),degrees.end());
    count.push_back(-1);
    for(int d:degrees)count.push_back(d);
    count.push_back(-2);count.push_back(card_diameter(g,omit));
    output[count]++;
  }
  return output;
}
int main(){
  for(auto [k,n]:vector<pair<int,int>>{{3,48},{3,49},{3,50},{3,51},{4,64}}){
    if(signature(build(k,n,0),k)!=signature(build(k,n,1),k)){
      cerr<<"FAIL k="<<k<<" n="<<n<<"\n";return 1;
    }
    cout<<"PASS k="<<k<<" n="<<n<<"\n";
  }
}
